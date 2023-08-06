from __future__ import absolute_import


import logging
import os
import socket
import select
import time

from ryu.lib.packet.icmp import ICMP_ECHO_REPLY
from ryu.lib.packet.ipv4 import ipv4
from ryu.lib.packet.packet import Packet

from contextlib import closing
from packy_agent.modules.base.socket import (get_seq_no, TIME_SIZE_BYTES,
                                             send_icmp_echo_request, decode_timestamp)


logger = logging.getLogger(__name__)


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

        ip_packet_data, (ip_address, _) = raw_socket.recvfrom(1024 + payload_len)

        packet = Packet(ip_packet_data, parse_cls=ipv4)

        icmp_packet = packet.protocols[1]
        logger.debug('Got ICMP packet type:{} code:{} from {}'.format(
            icmp_packet.type, icmp_packet.code, ip_address))
        if icmp_packet.type != ICMP_ECHO_REPLY:
            logger.debug('Discarded ICMP packet type:{} code:{} from {}'.format(
                icmp_packet.type, icmp_packet.code, ip_address))
            continue

        packet_seq = icmp_packet.data.seq
        packet_id = icmp_packet.data.id
        packet_payload = icmp_packet.data.data

        logger.debug(
            'ICMP packet from {} type:{} code:{} has id:{}, seq:{}, payload:{}'.format(
            ip_address, icmp_packet.type, icmp_packet.code, packet_id, packet_seq,
            packet_payload.encode('hex') if packet_payload else packet_payload))

        if packet_seq != seq_no or packet_id != id_:
            continue

        if packet_payload:
            packet_payload_len = len(packet_payload)
            if packet_payload_len != payload_len:
                logger.warning('Received payload length ({} bytes) differ from expected (sent) '
                               'length ({} bytes), but we are forgiving'.format(
                                packet_payload_len, payload_len))
                min_len = min(packet_payload_len, payload_len)
                if packet_payload[:min_len] != payload[:min_len]:
                    logger.debug('Discarded ICMP packet type:{} code:{} from {}: '
                                 'payload prefix differs'.format(icmp_packet.type,
                                                                 icmp_packet.code, ip_address))
                    continue
            elif packet_payload != payload:
                logger.debug('Discarded ICMP packet type:{} code:{} from {}: '
                             'payload differs'.format(icmp_packet.type, icmp_packet.code,
                                                      ip_address))
                continue

        if packet_payload and len(packet_payload) >= TIME_SIZE_BYTES:
            sent_time = decode_timestamp(packet_payload[:TIME_SIZE_BYTES])

        return finish_time - sent_time


def ping_once(destination_ip_address, timeout, packet_size_bytes=56):
    icmp_protocol = socket.getprotobyname('icmp')
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)) as raw_socket:
            id_ = os.getpid() & 0xFFFF
            seq_no = get_seq_no('icmp')
            sent_time, payload = send_icmp_echo_request(
                raw_socket, destination_ip_address, id_, seq_no, packet_size_bytes)
            return receive_icmp_reply(raw_socket, id_, seq_no, payload, timeout,
                                      sent_time=sent_time)

    except socket.error as (errno, msg):
        if errno == 1:  # Operation not permitted
            msg += ' - Note that ICMP messages can only be sent from processes running as root.'
            raise socket.error(msg)

        raise
