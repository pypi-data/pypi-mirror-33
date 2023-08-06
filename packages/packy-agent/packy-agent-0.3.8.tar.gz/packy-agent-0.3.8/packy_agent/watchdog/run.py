import argparse

from packy_agent.watchdog.service import WatchdogService
from packy_agent.utils.sentry import get_raven_client


def entry():
    raven_client = get_raven_client('watchdog')
    from packy_agent.watchdog import run as the_module

    parser = argparse.ArgumentParser(
        # Cannot use __name__, because when module is run as script it is equal to __main__
        prog='python -m {}'.format(the_module.__name__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.parse_args()

    service = WatchdogService(raven_client=raven_client)
    service.run()


if __name__ == '__main__':
    entry()
