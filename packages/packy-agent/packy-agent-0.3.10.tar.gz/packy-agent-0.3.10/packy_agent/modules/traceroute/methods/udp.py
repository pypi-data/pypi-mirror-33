from __future__ import absolute_import

import socket
import time
import logging
import select

from ryu.lib.packet.ipv4 import ipv4
from ryu.lib.packet.icmp import ICMP_TIME_EXCEEDED, ICMP_DEST_UNREACH, ICMP_PORT_UNREACH_CODE
from ryu.lib.packet.packet import Packet

from contextlib import closing
from packy_agent.modules.base.socket import TIME_SIZE_BYTES, encode_timestamp, decode_timestamp
from packy_agent.modules.base.constants import (
    IP_PACKET_HEADER_SIZE_BYTES, UDP_PACKET_HEADER_SIZE_BYTES)
from packy_agent.utils.misc import generate_random_string
from packy_agent.modules.traceroute.methods.base import guess_reply_hop_number


PACKET_HEADERS_SIZE_BYTES = IP_PACKET_HEADER_SIZE_BYTES + UDP_PACKET_HEADER_SIZE_BYTES

logger = logging.getLogger(__name__)


def send_udp_probe(raw_socket, destination_ip_address, port, ttl, packet_size_bytes=60,
                   payload=None):
    raw_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    sent_time = time.time()
    time_part = encode_timestamp(sent_time)
    if payload is None:
        if packet_size_bytes < PACKET_HEADERS_SIZE_BYTES:
            raise ValueError('payload_size_bytes must be greater or equal to {}'.format(
                PACKET_HEADERS_SIZE_BYTES))

        payload_size_bytes = packet_size_bytes - PACKET_HEADERS_SIZE_BYTES

        if payload_size_bytes < TIME_SIZE_BYTES:
            payload = generate_random_string(payload_size_bytes)
        else:
            payload = time_part + generate_random_string(payload_size_bytes - TIME_SIZE_BYTES)
    else:
        payload = time_part + payload

    raw_socket.sendto(payload, (destination_ip_address, port))
    logger.debug('Sent UDP packet to {}:{} (ttl:{}), payload: {}'.format(
        destination_ip_address, port, ttl, payload.encode('hex')))
    return sent_time, payload


def receive_icmp_reply_basic(raw_socket, recieve_bytes=2048):
    ip_packet_data, (ip_address, _) = raw_socket.recvfrom(recieve_bytes)

    packet = Packet(ip_packet_data, parse_cls=ipv4)

    ip_packet = packet.protocols[0]
    icmp_packet = packet.protocols[1]
    logger.debug('Got ICMP packet IP checksum:{} type:{} code:{} from {}'.format(
        packet.protocols[0].csum, icmp_packet.type, icmp_packet.code, ip_address))
    if icmp_packet.type == ICMP_TIME_EXCEEDED or (icmp_packet.type == ICMP_DEST_UNREACH and
                                                  icmp_packet.code == ICMP_PORT_UNREACH_CODE):
        inner_packet = Packet(icmp_packet.data.data, parse_cls=ipv4)
        udp_packet = inner_packet.protocols[1]
        if len(inner_packet.protocols) > 2:
            udp_payload = inner_packet.protocols[2]
        else:
            udp_payload = None

        if icmp_packet.type == ICMP_TIME_EXCEEDED:
            is_destination_reached = False
        elif icmp_packet.type == ICMP_DEST_UNREACH:
            # weird, but it means that destination is reached if we get a destination unreachable
            # ICMP packet with code ICMP_PORT_UNREACH_CODE
            is_destination_reached = True
        else:
            assert False, 'Should never get here'
            raise ValueError('Unsupported ICMP packet type: {} (should never get here)'.format(
                icmp_packet.type))

        return (ip_address, ip_packet, icmp_packet, udp_packet, udp_payload,
                is_destination_reached, True)
    else:
        return ip_address, ip_packet, icmp_packet, None, None, None, False


def does_payload_match(payload, udp_payload, icmp_packet, ip_address):
    payload_len = len(payload)
    if udp_payload:
        udp_payload_len = len(udp_payload)
        if udp_payload_len != payload_len:
            logger.warning('Received payload length ({} bytes) differ from expected (sent) '
                           'length ({} bytes), but we are forgiving'.format(
                udp_payload_len, payload_len))
            min_len = min(udp_payload_len, payload_len)
            if udp_payload[:min_len] != payload[:min_len]:
                logger.debug('Discarded ICMP packet type:{} code:{} from {}: '
                             'payload prefix differs'.format(icmp_packet.type,
                                                             icmp_packet.code, ip_address))
                return False
        elif udp_payload != payload:
            logger.debug('Discarded ICMP packet type:{} code:{} from {}: '
                         'payload differs'.format(icmp_packet.type, icmp_packet.code,
                                                  ip_address))
            return False

    return True


def get_sent_time_from_payload(udp_payload):
    if udp_payload and len(udp_payload) >= TIME_SIZE_BYTES:
        return decode_timestamp(udp_payload[:TIME_SIZE_BYTES])


def receive_icmp_reply(raw_socket, port, payload, timeout, sent_time):
    payload_len = len(payload)

    time_left = timeout
    while time_left > 0:
        start_time = time.time()
        ready_sockets = select.select((raw_socket,), (), (), time_left)
        finish_time = time.time()  # because by this time the entire packet is already in OS buffer
        time_left -= (finish_time - start_time)

        if not ready_sockets[0]:  # timeout
            break

        (ip_address, ip_packet, icmp_packet, udp_packet, udp_payload, is_destination_reached,
         is_probe_response) = receive_icmp_reply_basic(raw_socket, recieve_bytes=1024 + payload_len)

        if not is_probe_response:
            logger.debug('Discarded ICMP packet type:{} code:{} from {}'.format(
                icmp_packet.type, icmp_packet.code, ip_address))
            continue

        if udp_packet.dst_port != port:
            logger.debug('Discarded ICMP packet type:{} code:{} from {} '
                         '(UDP destination port {} does not match with original {})'.format(
                icmp_packet.type, icmp_packet.code, ip_address, udp_packet.dst_port, port))
            continue

        if not does_payload_match(payload, udp_payload, icmp_packet, ip_address):
            continue

        sent_time_from_payload = get_sent_time_from_payload(udp_payload)
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


def trace_hop_with_udp(destination_ip_address, port, timeout, ttl, packet_size_bytes=60):
    udp_protocol = socket.getprotobyname('udp')
    icmp_protocol = socket.getprotobyname('icmp')

    if callable(port):
        port = port()

    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp_protocol)) as udp_socket:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)) as icmp_socket:
                sent_time, payload = send_udp_probe(udp_socket, destination_ip_address, port, ttl,
                                                    packet_size_bytes)
                return receive_icmp_reply(icmp_socket, port, payload, timeout, sent_time=sent_time)
    except socket.error as (errno, msg):
        if errno == 1:  # Operation not permitted
            # TODO(dmu) HIGH: Fix to receive ICMP packet without being root
            msg += ' - process should be running as root.'
            raise socket.error(msg)

        raise
