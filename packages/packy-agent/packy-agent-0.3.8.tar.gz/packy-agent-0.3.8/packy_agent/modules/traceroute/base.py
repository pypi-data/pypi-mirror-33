from __future__ import absolute_import

import logging
import math
import socket
from functools import partial
from collections import namedtuple

from packy_agent.modules.traceroute.constants import (
    ICMP_METHOD, UDP_METHOD)
from packy_agent.modules.base.constants import IP_PACKET_HEADER_SIZE_BYTES, \
    ICMP_PACKET_HEADER_SIZE_BYTES, UDP_PACKET_HEADER_SIZE_BYTES
from packy_agent.modules.traceroute.methods.icmp import trace_hop_with_icmp
from packy_agent.modules.traceroute.methods.udp import trace_hop_with_udp
from packy_agent.modules.traceroute.types.parallel.base import traceroute_parallel
from packy_agent.modules.traceroute.types.sequential import traceroute_sequential

ProbeResult = namedtuple('ProbeResult', ('hop_number', 'reply_hop_number', 'probe_number',
                                         'hop_ip_address', 'rtt_seconds', 'is_destination_reached'))

MIN_ICMP_METHOD_PACKET_SIZE = IP_PACKET_HEADER_SIZE_BYTES + ICMP_PACKET_HEADER_SIZE_BYTES
MIN_UDP_METHOD_PACKET_SIZE = IP_PACKET_HEADER_SIZE_BYTES + UDP_PACKET_HEADER_SIZE_BYTES
RANGE_MIN = {
    ICMP_METHOD: MIN_ICMP_METHOD_PACKET_SIZE,
    UDP_METHOD: MIN_UDP_METHOD_PACKET_SIZE,
}
MAX_PACKET_SIZE = 1500

logger = logging.getLogger(__name__)


def aggregate_results(trace_results):
    agg_results = []
    for probe_results in trace_results:
        aggregated = {'loss': probe_results.count(None)}
        filtered_probe_results = filter(None, probe_results)
        if filtered_probe_results:
            # TODO(dmu) HIGH: Host may be different for the different probes of the same TTL
            representative_probe = filtered_probe_results[0]
            aggregated['host'] = representative_probe.hop_ip_address
            aggregated['reply_hop_number'] = representative_probe.reply_hop_number
            rtts = tuple(x.rtt_seconds for x in filtered_probe_results)
            aggregated['last'] = rtts[-1]
            aggregated['best'] = min(rtts)
            aggregated['worst'] = max(rtts)
            average = sum(rtts) / len(rtts)
            aggregated['average'] = average

            variance = sum((x - average) ** 2 for x in rtts) / len(rtts)
            aggregated['stdev'] = math.sqrt(variance)

        agg_results.append(aggregated)

    return agg_results


def traceroute(host, timeout=2, probe_count=1, packet_size_bytes=60, max_hops=100,
               method=UDP_METHOD, max_parallelism=10):

    if method not in (UDP_METHOD, ICMP_METHOD):
        raise ValueError('Unknown traceroute method: {}'.format(method))

    if max_parallelism < 1:
        raise ValueError('max_parallelism must be greater or equal to 1')

    range_min = RANGE_MIN[method]
    if not (range_min <= packet_size_bytes <= MAX_PACKET_SIZE):
        raise ValueError(
            'packet_size_bytes must be in range from {} to 1500 (inclusive)'.format(range_min))

    try:
        destination_ip_address = socket.gethostbyname(host)
    except socket.gaierror:
        logger.warning('Could not resolve {} to IP address'.format(host))
        return

    kwargs = {
        'destination_ip_address': destination_ip_address,
        'timeout': timeout,
        'packet_size_bytes': packet_size_bytes,
    }

    if max_parallelism == 1:
        if method == ICMP_METHOD:
            trace_function = trace_hop_with_icmp
        elif method == UDP_METHOD:
            port = [33434]

            def get_port():
                port[0] += 1
                return int(port[0])

            kwargs['port'] = get_port

            trace_function = trace_hop_with_udp
        else:
            assert False, 'Should never get here'
            raise ValueError('Unknown traceroute method: {}'.format(method))

        trace_function_partial = partial(trace_function, **kwargs)
        results = traceroute_sequential(trace_function_partial, destination_ip_address,
                                        probe_count=probe_count, max_hops=max_hops)
    else:
        results = traceroute_parallel(method, kwargs, destination_ip_address,
                                      probe_count=probe_count,
                                      max_hops=max_hops, timeout=timeout,
                                      max_parallelism=max_parallelism)

    return aggregate_results(results)
