import argparse
import sys
import os

from packy_agent.managers.install_and_upgrade import install_and_upgrade_manager
from packy_agent.configuration.agent.base import configuration as agent_configuration
from packy_agent.configuration.control_server.base import configuration as cs_configuration
from packy_agent.utils.logging import KNOWN_LOG_LEVELS, configure_basic_logging


ACTIVATE_SCRIPT_PATH = '/tmp/packy-activate.sh'
ACTIVATE_PACKY_AGENT_SH = """#!/usr/bin/env bash
source {venv_path}/bin/activate
packy-agent-activate
"""


def entry():
    from packy_agent.cli import welcome as the_module
    parser = argparse.ArgumentParser(
        # Cannot use __name__, because when module is run as script it is equal to __main__
        prog='python -m {}'.format(the_module.__name__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--log-level', default='INFO', choices=KNOWN_LOG_LEVELS)
    args = parser.parse_args()

    configure_basic_logging(level=args.log_level)

    print '\n' + '-' * 40 + '\n'
    print 'Welcome to Packy Agent'

    if not agent_configuration.is_activated():
        with open(ACTIVATE_SCRIPT_PATH, 'w') as f:
            f.write(ACTIVATE_PACKY_AGENT_SH.format(venv_path=os.getenv('VIRTUAL_ENV')))
        os.system('chmod u+x {}'.format(ACTIVATE_SCRIPT_PATH))

        link = install_and_upgrade_manager.get_control_server_link(
            cs_configuration.get_server_base_url())
        print ('Please, activate your Packy Agent at {} or '
               'run `sudo {}`\n'.format(link, ACTIVATE_SCRIPT_PATH))


if __name__ == '__main__':
    sys.exit(entry())
