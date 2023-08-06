from __future__ import absolute_import

import logging
import struct
import time

from ryu.lib.packet.icmp import icmp, echo
from ryu.lib.packet.packet import Packet

from packy_agent.utils.misc import generate_random_string

ICMP_PROTOCOL = 'icmp'

sequence = {
    ICMP_PROTOCOL: 1
}
logger = logging.getLogger(__name__)


def get_seq_no(proto):
    rv = sequence[proto]
    sequence[proto] += 1
    sequence[proto] &= 0xFFFF
    return rv


TIME_FORMAT = '<II'
TIME_SIZE_BYTES = struct.calcsize(TIME_FORMAT)


def encode_timestamp(timestamp):
    sent_time_seconds = int(timestamp)
    sent_time_microseconds = int((timestamp - sent_time_seconds) * 1000000)
    return struct.pack(TIME_FORMAT, sent_time_seconds, sent_time_microseconds)


def decode_timestamp(timestamp):
    sent_time_seconds, sent_time_microseconds = struct.unpack(TIME_FORMAT, timestamp)
    return sent_time_seconds + sent_time_microseconds / 1000000.


def send_icmp_echo_request(raw_socket, destination_ip_address, id_, seq_no, payload_size_bytes=56,
                           payload=None):
    sent_time = time.time()
    time_part = encode_timestamp(sent_time)
    if payload is None:
        if payload_size_bytes < 0:
            raise ValueError('payload_size_bytes must be greater or equal to 0')

        if payload_size_bytes < TIME_SIZE_BYTES:
            payload = generate_random_string(payload_size_bytes)
        else:
            payload = time_part + generate_random_string(payload_size_bytes - TIME_SIZE_BYTES)
    else:
        payload = time_part + payload

    packet = Packet()
    packet.add_protocol(icmp(data=echo(id_, seq_no, payload)))
    packet.serialize()

    raw_socket.sendto(packet.data, (destination_ip_address, 1))  # 1 - is a dummy port for ICMP
    logger.debug('Sent ICMP echo request({}) packet to {} with id:{} and seq:{}'.format(
        packet.protocols[0].type, destination_ip_address, id_, seq_no))
    return sent_time, payload
