from __future__ import print_function

import sys

from celery import Celery
from raven.contrib.celery import register_signal, register_logger_signal

from packy_agent.configuration.agent.base import configuration
from packy_agent.utils.misc import dump_version, remove_upgrade_in_progress_lock
from packy_agent.utils.sentry import get_raven_client


class CustomCelery(Celery):

    def __init__(self, *args, **kwargs):
        self.raven_client = kwargs.pop('raven_client', None)
        super(CustomCelery, self).__init__(*args, **kwargs)

    def gen_task_name(self, name, module):
        if self.main:
            return self.main + '.' + name

        return super(CustomCelery, self).gen_task_name(name, module)

    def on_configure(self):
        if self.raven_client:
            register_logger_signal(self.raven_client)
            register_signal(self.raven_client)


def get_celery_app(raven_client=None):
    agent_id = configuration.get_agent_id()
    if agent_id is None:
        return

    configuration.update_local_configuration_from_server()

    application = CustomCelery(configuration.get_tasks_prefix(), raven_client=raven_client)
    application.config_from_object(configuration.get_celery_configuration())

    __import__('packy_agent.tasks')  # register tasks

    return application


# Just creation of Raven Client logs to Sentry in case exception
app = get_celery_app(raven_client=get_raven_client('agent'))
remove_upgrade_in_progress_lock()
dump_version('/etc/packy-agent-version', 'PACKY_AGENT_VERSION')
if not app:
    # TODO(dmu) LOW: Provide a more elegant way to exit Celery until Agent is activated
    print('Packy Agent ID (packy.agent.agent_id) is not known (maybe agent has not '
          'been activated yet), will exit', file=sys.stderr)
    sys.exit(1)
