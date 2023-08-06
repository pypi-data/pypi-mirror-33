import logging

import os

from filelock import FileLock, Timeout


LOCKFILE_NAME_TEMPLATE = '/tmp/packy-agent.{}.lock'

logger = logging.getLogger(__name__)


def run_exclusive(task_function, args=(), kwargs=None, lock_name=None):
    kwargs = kwargs or {}

    file_lock = FileLock(LOCKFILE_NAME_TEMPLATE.format(lock_name or task_function.__name__))

    try:
        with file_lock.acquire(timeout=1):
            return task_function(*args, **kwargs)
    except Timeout:
        logger.warning('Parallel `{}` task detected, exiting'.format(task_function.__name__))
        try:
            file_lock.acquire(timeout=300)
            file_lock.release()
        except Timeout:
            lock_file = file_lock.lock_file
            logger.warning('Self-healing: force deletion of lock file: {}'.format(lock_file))
            try:
                os.remove(lock_file)
            except OSError:
                pass
