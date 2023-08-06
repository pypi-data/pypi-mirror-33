import argparse
import sys

from packy_agent.managers.install_and_upgrade import install_and_upgrade_manager, CONFIGURE_TARGETS
from packy_agent.utils.logging import KNOWN_LOG_LEVELS, configure_basic_logging


# TODO(dmu) HIGH: Stopping keeping this code once all agent upgrade to v0.3.4 or higher
def entry():
    from packy_agent.cli import configure as the_module
    parser = argparse.ArgumentParser(
        # Cannot use __name__, because when module is run as script it is equal to __main__
        prog='python -m {}'.format(the_module.__name__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('target', choices=CONFIGURE_TARGETS)
    parser.add_argument('base_url')
    parser.add_argument('--log-level', default='DEBUG', choices=KNOWN_LOG_LEVELS)
    args = parser.parse_args()

    configure_basic_logging(level=args.log_level)

    install_and_upgrade_manager.install_and_restart()


if __name__ == '__main__':
    sys.exit(entry())
