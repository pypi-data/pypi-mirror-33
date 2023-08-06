from __future__ import absolute_import

import raven

import logging
import packy_agent
from packy_agent.utils.misc import is_inside_docker_container
from packy_agent.configuration.agent.base import configuration

logger = logging.getLogger(__name__)


def get_raven_client(component_name):
    packy_agent_sentry_dsn = configuration.get_packy_agent_sentry_dsn()

    if packy_agent_sentry_dsn:
        agent_id = configuration.get_agent_id()
        name = '[{}, {}] {}'.format(
            # TODO(dmu) MEDIUM: Improve OS/platform reporting
            component_name, 'Docker' if is_inside_docker_container() else 'non-Docker',
            'Inactive agent' if agent_id is None else 'Agent ID: {}'.format(agent_id))

        return raven.Client(
            packy_agent_sentry_dsn,
            name=name,
            release=packy_agent.__version__,
            environment=configuration.get_server_base_url() or ''
        )
    else:
        logger.warning('Sentry DSN is not configured')
