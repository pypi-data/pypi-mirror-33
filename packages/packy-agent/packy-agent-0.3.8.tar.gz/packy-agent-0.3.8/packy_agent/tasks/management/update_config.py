import logging

from celery import shared_task

from packy_agent.configuration.agent.base import configuration
from packy_agent.managers.control import control_manager

logger = logging.getLogger(__name__)


@shared_task()
def update_config():
    configuration.update_local_configuration_from_server()
    control_manager.restart_control_server()
    control_manager.restart_watchdog()
