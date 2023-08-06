from __future__ import absolute_import

import os
import select
import socket
import time
import logging
from contextlib import closing

from ryu.lib.packet.icmp import ICMP_ECHO_REPLY, ICMP_TIME_EXCEEDED
from ryu.lib.packet.ipv4 import ipv4
from ryu.lib.packet.packet import Packet

from packy_agent.modules.base.socket import (get_seq_no, TIME_SIZE_BYTES,
    send_icmp_echo_request as send_icmp_probe, decode_timestamp)
from packy_agent.modules.base.constants import (IP_PACKET_HEADER_SIZE_BYTES,
    ICMP_PACKET_HEADER_SIZE_BYTES)
from packy_agent.modules.traceroute.methods.base import guess_reply_hop_number


PACKET_HEADERS_SIZE_BYTES = IP_PACKET_HEADER_SIZE_BYTES + ICMP_PACKET_HEADER_SIZE_BYTES

logger = logging.getLogger(__name__)


def receive_icmp_reply_basic(raw_socket, id_, recieve_bytes=2048):
    ip_packet_data, (ip_address, _) = raw_socket.recvfrom(recieve_bytes)

    packet = Packet(ip_packet_data, parse_cls=ipv4)

    ip_packet = packet.protocols[0]
    icmp_packet = packet.protocols[1]
    logger.debug('Got ICMP packet type:{} code:{} from {}'.format(
        icmp_packet.type, icmp_packet.code, ip_address))
    if icmp_packet.type in (ICMP_TIME_EXCEEDED, ICMP_ECHO_REPLY):
        if icmp_packet.type == ICMP_TIME_EXCEEDED:
            inner_packet = Packet(icmp_packet.data.data, parse_cls=ipv4)
            effective_icmp_packet = inner_packet.protocols[1]
            is_destination_reached = False
        elif icmp_packet.type == ICMP_ECHO_REPLY:
            effective_icmp_packet = icmp_packet
            is_destination_reached = True
        else:
            assert False, 'Should never get here'
            raise ValueError('Unsupported ICMP packet type: {}'.format(icmp_packet.type))

        effective_id = effective_icmp_packet.data.id
        if effective_id != id_:
            return ip_address, ip_packet, icmp_packet, None, None, False

        effective_seq = effective_icmp_packet.data.seq
        effective_payload = effective_icmp_packet.data.data

        logger.debug(
            'ICMP packet from {} type:{} code:{} has effective id:{}, seq:{}, payload:{}'.format(
                ip_address, icmp_packet.type, icmp_packet.code, effective_id, effective_seq,
                effective_payload.encode('hex') if effective_payload else effective_payload))

        return (ip_address, ip_packet, icmp_packet, effective_icmp_packet, is_destination_reached,
                True)
    else:
        return ip_address, ip_packet, icmp_packet, None, None, False


def does_payload_match(payload, effective_payload, icmp_packet, ip_address):
    payload_len = len(payload)
    if effective_payload:
        effective_payload_len = len(effective_payload)
        if effective_payload_len != payload_len:
            logger.warning('Received payload length ({} bytes) differ from expected (sent) '
                           'length ({} bytes), but we are forgiving'.format(
                effective_payload_len, payload_len))
            min_len = min(effective_payload_len, payload_len)
            if effective_payload[:min_len] != payload[:min_len]:
                logger.debug('Discarded ICMP packet type:{} code:{} from {}: '
                             'payload prefix differs'.format(icmp_packet.type,
                                                             icmp_packet.code, ip_address))
                return False
        elif effective_payload != payload:
            logger.debug('Discarded ICMP packet type:{} code:{} from {}: '
                         'payload differs'.format(icmp_packet.type, icmp_packet.code,
                                                  ip_address))
            return False

    return True


def get_sent_time_from_payload(effective_payload):
    if effective_payload and len(effective_payload) >= TIME_SIZE_BYTES:
        return decode_timestamp(effective_payload[:TIME_SIZE_BYTES])


def receive_icmp_reply(raw_socket, id_, seq_no, payload, timeout, sent_time):
    payload_len = len(payload)

    time_left = timeout
    while time_left > 0:
        start_time = time.time()
        ready_sockets = select.select((raw_socket,), (), (), time_left)
        finish_time = time.time()  # because by this time the entire packet is already in OS buffer
        time_left -= (finish_time - start_time)

        if not ready_sockets[0]:  # timeout
            break

        (ip_address, ip_packet, icmp_packet, effective_icmp_packet, is_destination_reached,
         is_probe_response) = receive_icmp_reply_basic(raw_socket, id_, 1024 + payload_len)

        if not is_probe_response:
            logger.debug('Discarded ICMP packet type:{} code:{} from {}'.format(
                icmp_packet.type, icmp_packet.code, ip_address))
            continue

        effective_seq = effective_icmp_packet.data.seq
        effective_payload = effective_icmp_packet.data.data

        if effective_seq != seq_no:
            continue

        if not does_payload_match(payload, effective_payload, icmp_packet, ip_address):
            continue

        sent_time_from_payload = get_sent_time_from_payload(effective_payload)
        if sent_time_from_payload is not None:
            sent_time = sent_time_from_payload

        from packy_agent.modules.traceroute.base import ProbeResult
        return ProbeResult(
            hop_number=None,
            reply_hop_number=guess_reply_hop_number(ip_packet.ttl),
            probe_number=None,
            hop_ip_address=ip_address,
            rtt_seconds=finish_time - sent_time,
            is_destination_reached=is_destination_reached)


def trace_hop_with_icmp(destination_ip_address, timeout, ttl, packet_size_bytes=60):
    icmp_protocol = socket.getprotobyname('icmp')
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)) as raw_socket:
            raw_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

            id_ = os.getpid() & 0xFFFF
            seq_no = get_seq_no('icmp')
            sent_time, payload = send_icmp_probe(
                raw_socket, destination_ip_address, id_, seq_no,
                packet_size_bytes - PACKET_HEADERS_SIZE_BYTES)
            return receive_icmp_reply(raw_socket, id_, seq_no, payload, timeout,
                                      sent_time=sent_time)

    except socket.error as (errno, msg):
        if errno == 1:  # Operation not permitted
            msg += ' - Note that ICMP messages can only be sent from processes running as root.'
            raise socket.error(msg)

        raise
