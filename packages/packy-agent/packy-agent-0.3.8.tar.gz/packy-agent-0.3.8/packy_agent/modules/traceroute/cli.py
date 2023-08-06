import argparse
import logging
import sys

from packy_agent.modules.traceroute import base
from packy_agent.modules.traceroute.constants import TRACEROUTE_METHODS, UDP_METHOD


def do_traceroute(host, timeout=1, probe_count=1, packet_size_bytes=60, max_hops=30,
                  method=UDP_METHOD, max_parallelism=1):
    agg_results = base.traceroute(host, timeout=timeout, probe_count=probe_count,
                                  packet_size_bytes=packet_size_bytes, max_hops=max_hops,
                                  method=method, max_parallelism=max_parallelism)
    if not agg_results:
        print 'No results'
        return

    for x, result in enumerate(agg_results):
        print x + 1, result.get('host'), result


def entry():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARNING)

    from packy_agent.modules.traceroute import cli as the_module

    parser = argparse.ArgumentParser(
        # Cannot use __name__, because when module is run as script it is equal to __main__
        prog='python -m {}'.format(the_module.__name__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('host')
    parser.add_argument('--max-hops', help='max hops', type=int, default=30)
    parser.add_argument('--probe-count', help='probe count', type=int, default=3)
    parser.add_argument('--packet-size-bytes', help='IP packet size in bytes',
                        type=int, default=60)
    parser.add_argument('--max-parallelism', help='max parallelism', type=int, default=1)
    parser.add_argument('--timeout', help='timout', type=float, default=1)
    parser.add_argument('-M', '--method', help='method', choices=TRACEROUTE_METHODS,
                        default=UDP_METHOD)

    args = parser.parse_args()

    return do_traceroute(args.host, timeout=args.timeout, probe_count=args.probe_count,
                         packet_size_bytes=args.packet_size_bytes,
                         max_hops=args.max_hops, method=args.method,
                         max_parallelism=args.max_parallelism)


if __name__ == '__main__':
    sys.exit(entry())
