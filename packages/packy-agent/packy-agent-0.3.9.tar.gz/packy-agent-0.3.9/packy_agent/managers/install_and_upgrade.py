import logging
import os
import os.path
from urllib import urlencode

from filelock import FileLock, Timeout
from jinja2 import Template
from pkg_resources import parse_version

from packy_agent.clients.packy_server import PackyServerClient
from packy_agent.clients.packy_server import packy_server_client_factory
from packy_agent.configuration.agent.base import configuration as packy_agent_configuration
from packy_agent.configuration.control_server.base import configuration
from packy_agent.exceptions import AuthenticationError, ValidationError
from packy_agent.managers.control import control_manager
from packy_agent.utils.auth import is_activated
from packy_agent.utils.misc import run_shell_command_async, is_inside_docker_container, \
    UPGRADE_IN_PROGRESS_FILE_LOCK
from packy_agent.utils.network import get_machine_ip_address, get_hostname_from_url
from packy_agent.utils.output import write_to_console_or_file
from packy_agent.utils.pkg_resources import get_package_file_content

logger = logging.getLogger(__name__)

UBUNTU_CONFIGURE_TARGET = 'ubuntu'
DOCKER_CONFIGURE_TARGET = 'docker'
CONFIGURE_TARGETS = (UBUNTU_CONFIGURE_TARGET, DOCKER_CONFIGURE_TARGET)
PACKY_GET_INSTALL_SCRIPT_PATH = '/tmp/packy-get-install-script.sh'


def render_template_from_package_file_content(template_module_name, template_filename,
                                              context=None):
    template_text = get_package_file_content(template_module_name, template_filename)
    template = Template(template_text)
    return template.render(**(context or {}))


class InstallAndUpgradeManager(object):

    def activate(self, email, password, agent_id=None, async_restart=True):
        if is_activated():
            raise ValidationError('Agent has already been activated')

        client = PackyServerClient(configuration.get_server_base_url(), agent_id=agent_id)
        if agent_id is None:
            response = client.create_agent(email, password)
        else:
            response = client.activate_agent(email, password)
        status_code = response.status_code
        if status_code == 401:
            raise AuthenticationError('Invalid credentials for agent activation')
        elif status_code == 400:
            payload = response.json()
            errors = payload.get('errors') or {}
            non_field_errors = errors.pop('non_field_errors', None) or []
            messages = ([payload.get('message')] + non_field_errors +
                        ['{}: {}.'.format(k, v) for k, v in errors.iteritems()])

            raise ValidationError(' '.join(filter(None, messages)))

        response.raise_for_status()

        agent_configuration = response.json()['configuration']
        packy_agent_configuration.save_local_configuration(agent_configuration)

        # TODO(dmu) LOW: Instead of always restart do according to current running status
        control_manager.restart_packy_agent(delay_seconds=1 if async_restart else None)

    def install_and_restart(self, version=None, delay_seconds=None):
        logger.info('Upgrading...')
        if not configuration.is_upgrade_enabled():
            logger.info('Upgrade was disabled (for developer protection)')
            return

        file_lock = FileLock(UPGRADE_IN_PROGRESS_FILE_LOCK)
        try:
            with file_lock.acquire(timeout=1):
                client = packy_server_client_factory.get_client_by_configuration(
                    packy_agent_configuration)
                version_max = client.get_version_max()
                if version is None:
                    version = version_max
                else:
                    if version_max and parse_version(version) > parse_version(version_max):
                        raise ValueError('Could not install/upgrade to version {} '
                                         '(it is higher than {})'.format(version, version_max))

                # TODO(dmu) HIGH: Improve OS detection
                operating_system = 'alpine' if is_inside_docker_container() else 'ubuntu'
                download_args = {'os': operating_system}
                if version:
                    download_args['version'] = version

                write_to_console_or_file(
                    PACKY_GET_INSTALL_SCRIPT_PATH,
                    render_template_from_package_file_content(
                        'packy_agent', 'scripts/misc/packy-get-install-script.sh.j2',
                        {'with_shebang': True,
                         'download_args': '?{}'.format(urlencode(download_args))}))

                # Restart is done in the install script
                extra_envvars = {'PACKY_SERVER_BASE_URL': "'{}'".format(
                    configuration.get_server_base_url().rstrip('/'))}

                packy_agent_pypi_repository = configuration.get_packy_agent_pypi_repository()
                if packy_agent_pypi_repository:
                    extra_envvars['PIP_EXTRA_ARGS'] = "'--extra-index-url {}'".format(
                        packy_agent_pypi_repository)

                if os.getenv('OLD_PATH'):
                    extra_envvars['PATH'] = '$OLD_PATH'

                command = '{} /bin/bash {}; rm -f {}'.format(
                    ' '.join('export {}={};'.format(k, v) for k, v in extra_envvars.iteritems()),
                    PACKY_GET_INSTALL_SCRIPT_PATH, UPGRADE_IN_PROGRESS_FILE_LOCK)

                run_shell_command_async(command, delay_seconds=delay_seconds)
        except Timeout:
            logger.warning('Concurrent upgrade detected')

    def upgrade_and_restart(self, delay_seconds=None):
        self.install_and_restart(delay_seconds=delay_seconds)

    # TODO(dmu) MEDIUM: Refactor to use Ansible for most of these stuff
    def get_control_server_link(self, packy_server_base_url):
        # TODO(dmu) LOW: Unhardcode schema: `http://`
        link = 'http://' + get_machine_ip_address(get_hostname_from_url(packy_server_base_url))
        port = configuration.get_control_server_port()
        if port != 80:
            link += ':{}'.format(port)

        return link


install_and_upgrade_manager = InstallAndUpgradeManager()
