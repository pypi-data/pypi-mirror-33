import logging

from celery import shared_task
from retry.api import retry_call

from packy_agent.clients.packy_server import packy_server_client_factory
from packy_agent.configuration.agent.base import configuration
from packy_agent.modules.traceroute.base import traceroute
from packy_agent.tasks.modules.base import run_exclusive
from packy_agent.modules.traceroute.constants import UDP_METHOD
from packy_agent.utils.misc import get_iso_format_utcnow

logger = logging.getLogger(__name__)


def convert_to_hops(traceroute_result, probe_count):
    hops = []
    for x, item in enumerate(traceroute_result):
        hop = {
            'host': item.get('host'),
            'number': x + 1,
            'reply_number': item.get('reply_hop_number'),
            'loss': round(100.0 * item['loss'] / probe_count, 1),
            'sent': probe_count,
        }
        for attr in ('last', 'average', 'best', 'worst', 'stdev'):
            value = item.get(attr)
            if value is not None:
                hop[attr] = round(value * 1000.0, 1)

        hops.append(hop)

    return hops


def trace(host):
    module_config = configuration.get_trace_module_configuration()

    start_time = get_iso_format_utcnow()
    probe_count = module_config['number_of_pings']
    packet_size_bytes = module_config['packet_size']
    if not (28 <= packet_size_bytes <= 1500):
        packet_size_bytes = min(max(28, packet_size_bytes), 1500)
        logger.warning('`packet_size` is out of range from 28 to 1500 (inclusive), '
                       'value is adjusted to {}'.format(packet_size_bytes))

    result = traceroute(host, probe_count=probe_count,
                        packet_size_bytes=packet_size_bytes,
                        max_hops=module_config['ttl'],
                        method=module_config.get('method', UDP_METHOD),
                        max_parallelism=module_config.get('parallelism', 16))
    if result is None:
        return

    # TODO(dmu) HIGH: Producing of result structure should be moved to PackyServerClient level
    return {
        'target': host,
        'packet_size': module_config['packet_size'],
        'pings': module_config['number_of_pings'],
        'time': start_time,
        'hops': convert_to_hops(result, probe_count),
    }


def trace_all_impl():
    hosts = configuration.get_trace_module_configuration().get('hosts')
    if not hosts:
        logger.warning('Trace hosts are not configured')
        # TODO(dmu) HIGH: Should I mark task as failed?
        return

    client = packy_server_client_factory.get_client_by_configuration(configuration)
    # See comment for speedtest
    for host in hosts:
        result = trace(host)
        if result is None:
            continue

        retry_call(client.submit_trace_measurement, (result,),
                   tries=configuration.get_submit_retries())


@shared_task
def trace_all():
    run_exclusive(trace_all_impl)
