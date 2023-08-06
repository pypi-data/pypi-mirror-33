from __future__ import absolute_import

import logging
import os
import socket
import time
import select
from collections import defaultdict
from contextlib import closing
from collections import namedtuple

from packy_agent.modules.base.socket import get_seq_no, send_icmp_echo_request as send_icmp_probe
from packy_agent.modules.traceroute.constants import ICMP_METHOD, UDP_METHOD
from packy_agent.modules.traceroute.methods.icmp import (
    PACKET_HEADERS_SIZE_BYTES as ICMP_METHOD_PACKET_HEADERS_SIZE_BYTES)
from packy_agent.modules.traceroute.methods.udp import send_udp_probe
from packy_agent.modules.traceroute.types.parallel.udp import process_udp_probe
from packy_agent.modules.traceroute.types.parallel.icmp import process_icmp_probe

logger = logging.getLogger(__name__)
SentProbe = namedtuple('SentProbe', ('ttl', 'probe_number', 'sent_time', 'payload'))


def get_ttl_and_probe_number(max_hops, probe_count):
    for ttl in xrange(1, max_hops + 1):
        for probe_number in xrange(probe_count):
            yield (ttl, probe_number)


def receive_probe(method, sent_probes, icmp_socket, id_=None, timeout=0.001):
    ready_sockets = select.select((icmp_socket,), (), (), timeout)
    # because by this time the entire packet is already in OS buffer
    finish_time = time.time()

    if ready_sockets[0]:
        if method == UDP_METHOD:
            return_value = process_udp_probe(sent_probes, icmp_socket, finish_time)
        elif method == ICMP_METHOD:
            return_value = process_icmp_probe(sent_probes, id_, icmp_socket, finish_time)
        else:
            raise ValueError('Unknown traceroute method: {}'.format(method))
    else:  # timeout
        return_value = None

    return return_value


def traceroute_parallel_impl(method, send_socket, icmp_socket,
                             kwargs, destination_ip_address, probe_count,
                             max_hops=100, timeout=2, max_parallelism=10):
    if method == UDP_METHOD:
        # TODO(dmu) LOW: Improve to reuse ports once they are not needed any more
        port = 33434
        receive_probe_kwargs = {}
    elif method == ICMP_METHOD:
        id_ = os.getpid() & 0xFFFF
        receive_probe_kwargs = {'id_': id_}
    else:
        raise ValueError('Unknown traceroute method: {}'.format(method))

    destination_hop_number = max_hops
    sent_probes = {}
    results = defaultdict(dict)
    is_done = False
    should_send = True
    ttl_and_probe_number_generator = get_ttl_and_probe_number(max_hops, probe_count)
    while not is_done:
        if should_send and len(sent_probes) < max_parallelism:
            try:
                ttl, probe_number = next(ttl_and_probe_number_generator)
                should_send = ttl <= destination_hop_number
            except StopIteration:
                should_send = False

            if should_send:
                if method == UDP_METHOD:
                    sent_time, sent_payload = send_udp_probe(
                        send_socket, destination_ip_address=kwargs['destination_ip_address'],
                        port=port, ttl=ttl, packet_size_bytes=kwargs['packet_size_bytes'])
                    sent_probes[port] = SentProbe(ttl, probe_number, sent_time, sent_payload)
                    port += 1
                elif method == ICMP_METHOD:
                    icmp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                    seq_no = get_seq_no('icmp')
                    sent_time, sent_payload = send_icmp_probe(
                        send_socket, destination_ip_address, id_, seq_no,
                        kwargs['packet_size_bytes'] - ICMP_METHOD_PACKET_HEADERS_SIZE_BYTES)
                    sent_probes[seq_no] = SentProbe(ttl, probe_number, sent_time, sent_payload)
                else:
                    raise ValueError('Unknown traceroute method: {}'.format(method))

        while True:
            received_probe = receive_probe(
                method, sent_probes, icmp_socket, **receive_probe_kwargs)

            if not received_probe:
                break

            results[received_probe.hop_number][received_probe.probe_number] = received_probe

            if (received_probe.is_destination_reached or
                    received_probe.hop_ip_address == destination_ip_address):
                destination_hop_number = min(received_probe.hop_number, destination_hop_number)

            for ttl_local in xrange(destination_hop_number, 0, -1):
                if len(results[ttl_local]) < probe_count:
                    break
            else:
                is_done = True
                break

        for sent_probe_key, sent_probe in sent_probes.items():
            if sent_probe.sent_time + timeout <= time.time():
                if method == UDP_METHOD:
                    logger.debug('Probe on port {} timed out'.format(sent_probe_key))
                elif method == ICMP_METHOD:
                    logger.debug('Probe with seq {} timed out'.format(sent_probe_key))
                else:
                    raise ValueError('Unknown traceroute method: {}'.format(method))

                del sent_probes[sent_probe_key]

        if not should_send and not sent_probes:
            is_done = True

    return [[results[ttl].get(probe_number) for probe_number in xrange(probe_count)]
            for ttl in xrange(1, destination_hop_number + 1)]


def traceroute_parallel(method, kwargs, destination_ip_address, probe_count,
                        max_hops=100, timeout=2, max_parallelism=10):

    udp_protocol = socket.getprotobyname('udp')
    icmp_protocol = socket.getprotobyname('icmp')

    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)) as icmp_socket:
            if method == UDP_METHOD:
                with closing(socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM, udp_protocol)) as udp_socket:
                    return traceroute_parallel_impl(
                        method, send_socket=udp_socket, icmp_socket=icmp_socket,
                        kwargs=kwargs, destination_ip_address=destination_ip_address,
                        probe_count=probe_count, max_hops=max_hops, timeout=timeout,
                        max_parallelism=max_parallelism)
            elif method == ICMP_METHOD:
                return traceroute_parallel_impl(
                    method, send_socket=icmp_socket, icmp_socket=icmp_socket,
                    kwargs=kwargs, destination_ip_address=destination_ip_address,
                    probe_count=probe_count, max_hops=max_hops, timeout=timeout,
                    max_parallelism=max_parallelism)
            else:
                raise ValueError('Unknown traceroute method: {}'.format(method))

    except socket.error as (errno, msg):
        if errno == 1:  # Operation not permitted
            # TODO(dmu) HIGH: Fix to receive ICMP packet without being root
            msg += ' - process should be running as root.'
            raise socket.error(msg)

        raise
