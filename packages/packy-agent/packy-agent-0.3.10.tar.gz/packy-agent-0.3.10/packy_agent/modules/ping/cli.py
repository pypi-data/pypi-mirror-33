import argparse
import logging
import sys
import time
import socket

from packy_agent.modules.ping import base


def do_ping(host, timeout=1, ping_count=None, interval_seconds=1, packet_size_bytes=56):
    try:
        destination_ip_address = socket.gethostbyname(host)
    except socket.gaierror:
        print 'Could not resolve {} to IP address'.format(host)
        return

    print 'PING {} ({})'.format(host, destination_ip_address)
    no = 1
    while ping_count is None or ping_count > 0:
        rtt_seconds = base.ping_once(host, timeout=timeout, packet_size_bytes=packet_size_bytes)
        print '{0} time={1:.2f} ms'.format(no, round(rtt_seconds * 1000, 2))

        no += 1
        if ping_count is not None:
            ping_count -= 1

        time.sleep(interval_seconds)


def entry():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    from packy_agent.modules.traceroute import cli as the_module

    parser = argparse.ArgumentParser(
        # Cannot use __name__, because when module is run as script it is equal to __main__
        prog='python -m {}'.format(the_module.__name__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('host')
    parser.add_argument('--ping-count', type=int, default=None)
    parser.add_argument('--packet-size-bytes', help='ICMP payload size in bytes',
                        type=int, default=56)
    parser.add_argument('--interval-seconds', type=float, default=1)
    parser.add_argument('--timeout', type=float, default=1)

    args = parser.parse_args()

    return do_ping(args.host, timeout=args.timeout, ping_count=args.ping_count,
                   interval_seconds=args.interval_seconds,
                   packet_size_bytes=args.packet_size_bytes)


if __name__ == '__main__':
    sys.exit(entry())
