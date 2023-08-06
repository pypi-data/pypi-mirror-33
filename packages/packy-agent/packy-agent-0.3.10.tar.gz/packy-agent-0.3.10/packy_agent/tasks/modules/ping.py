import logging
import socket
import time

from celery import shared_task
from retry.api import retry_call

from packy_agent.clients.packy_server import packy_server_client_factory
from packy_agent.configuration.agent.base import configuration
from packy_agent.modules.ping.base import ping_once
from packy_agent.tasks.modules.base import run_exclusive
from packy_agent.utils.misc import get_iso_format_utcnow

logger = logging.getLogger(__name__)


def ping(host):
    module_config = configuration.get_ping_module_configuration()

    number_of_pings = module_config['number_of_pings']
    packet_size = module_config['packet_size']
    interval_ms = module_config.get('interval_ms', 0)
    start_time = get_iso_format_utcnow()
    pings = []

    try:
        destination_ip_address = socket.gethostbyname(host)
    except socket.gaierror:
        logger.warning('Could not resolve {} to IP address'.format(host))
    else:
        for _ in xrange(number_of_pings):
            start = time.time()
            try:
                rtt_seconds = ping_once(destination_ip_address, 10, packet_size_bytes=packet_size)
                if rtt_seconds is None:
                    continue
            except Exception:
                logger.warning('Error during ping', exc_info=True)
                continue

            pings.append(round(rtt_seconds * 1000, 2))

            time_left = interval_ms / 1000. - (time.time() - start)
            if time_left > 0:
                logger.debug('Waiting {0:.03f} seconds for next ping'.format(time_left))
                time.sleep(time_left)

    # TODO(dmu) HIGH: Producing of result structure should be moved to PackyServerClient level
    return {
        'target': host,
        'packet_size': packet_size,
        'n_pings': number_of_pings,
        'time': start_time,
        'pings': ','.join(map(str, pings))
    }


def ping_all_impl():
    hosts = configuration.get_ping_module_configuration().get('hosts')
    if not hosts:
        logger.warning('Ping hosts are not configured')
        # TODO(dmu) HIGH: Should I mark task as failed?
        return

    client = packy_server_client_factory.get_client_by_configuration(configuration)
    # See comment for speedtest
    for host in hosts:
        result = ping(host)
        retry_call(client.submit_ping_measurement, (result,),
                   tries=configuration.get_submit_retries())


@shared_task
def ping_all():
    run_exclusive(ping_all_impl)
