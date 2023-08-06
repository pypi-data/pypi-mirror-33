# -*- coding: utf-8 -*-
"""
| **@created on:** 30/06/18,
| **@author:** prathyushsp,
| **@version:** v0.0.1
|
| **Description:**
| Monitor Module
|
| **Sphinx Documentation Status:** --
|
..todo::
"""

__all__ = ['Monitor']

from threading import Thread
import typing
import psutil
import pmark.string_constants as constants
import logging
import time
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class Monitor(Thread, metaclass=ABCMeta):
    """
    | **@author:** Prathyush SP
    |
    | Benchmark Monitors
    """

    def __init__(self, pid: int, interval_in_secs: typing.Union[int, float], monitor_type: str):
        """

        :param pid: Process Id
        :param interval_in_secs: Interval in seconds
        :param monitor_type: Monitor Type
        """
        super().__init__()
        self.monitor_type = monitor_type
        self.monitor_disabled = False
        self.pid = pid
        self.interval = interval_in_secs
        self.process_status = None
        self.psutil_process = None
        self.validate()

    def _check_process_status(self):
        """
        | **@author:** Prathyush SP
        |
        | Check status of pid which is monitored
        :return: True / False based on conditions
        """
        self.process_status = self.psutil_process.status()
        return psutil.pid_exists(self.pid) and self.psutil_process.is_running() \
               and not (self.psutil_process.status() == psutil.STATUS_ZOMBIE
                        or self.psutil_process.status() == psutil.STATUS_DEAD
                        or self.psutil_process.status() == psutil.STATUS_STOPPED) and not self.monitor_disabled

    def run(self):
        """
        | **@author:** Prathyush SP
        |
        | Thread.start() implementation.
        """
        if self.monitor_disabled:
            self.process_status = constants.Monitors.Code.Disabled
            logger.error('Monitor disabled due to error . . .')
        else:
            try:
                logger.debug('Starting {} . . .'.format(self.monitor_type))
                while self._check_process_status():
                    logger.debug('Running {} . . .'.format(self.monitor_type))
                    self.monitor_running()
                    time.sleep(self.interval)
                self.monitor_stopped()
                self.process_status = constants.Monitors.Code.Completed if self.psutil_process.wait() == 0 else constants.Monitors.Code.Error
                logger.debug('Process Exited. Stopping {}  . . .'.format(self.monitor_type))
            except Exception as e:
                self.monitor_stopped()
                self.process_status = constants.Monitors.Code.Error
                logger.debug('Encountered {}. Stopping {}'.format(e, self.monitor_type))

    @abstractmethod
    def monitor_running(self):
        """
        | **@author:** Prathyush SP
        |
        | Initialize / Update monitor variables during runtime
        """
        pass  # pragma: no cover

    @abstractmethod
    def monitor_stopped(self):
        """
        | **@author:** Prathyush SP
        |
        | Initialize / Update monitor variables on stop
        """
        pass  # pragma: no cover

    @abstractmethod
    def monitor_stats(self):
        """
        | **@author:** Prathyush SP
        |
        :return - Monitor Statistics
        """
        pass  # pragma: no cover

    def validate(self):
        """
        | **@author:** Prathyush SP
        |
        | BenchmarkMonitor
        :return:
        """
        if self.interval < 1:
            self.interval = 1
            logger.debug('Minimum supported interval is 1 seconds')
        if psutil.pid_exists(self.pid):
            self.psutil_process = psutil.Process(self.pid)
            self.process_status = constants.Monitors.Code.Initializing
        else:
            logger.debug('Process does not exist')
            self.monitor_disabled = True
            self.process_status = 'ERROR'
