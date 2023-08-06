# -*- coding: utf-8 -*-
"""
| **@created on:** 30/06/18,
| **@author:** prathyushsp,
| **@version:** v0.0.1
|
| **Description:**
| Memory Monitor Module
|
| **Sphinx Documentation Status:** --
|
..todo::
"""

__all__ = ['MemoryMonitor']

from pmark.monitors.monitor import Monitor
import typing
import pmark.string_constants as constants
from collections import OrderedDict
import psutil


class MemoryMonitor(Monitor):
    """
    | **@author:** Prathyush SP
    |
    | Memory Monitor
    """

    def __init__(self, pid: int, interval_in_secs: typing.Union[int, float] = 1):
        """

        :param pid:
        :param interval_in_secs:
        """
        Monitor.__init__(self, pid=pid, interval_in_secs=interval_in_secs,
                         monitor_type=constants.Monitors.Type.MemoryMonitor)
        self.memory_usage_per_second = []
        self.max_memory_usage = None

    def monitor_running(self):
        """
        | **@author:** Prathyush SP
        |
        | Initialize / Update monitor variables during runtime
        """
        self.memory_usage_per_second.append(self.psutil_process.memory_info().rss / 2 ** 20)

    def monitor_stopped(self):
        """
        | **@author:** Prathyush SP
        |
        | Initialize / Update monitor variables on stop
        """
        self.max_memory_usage = float(max(self.memory_usage_per_second)) if self.memory_usage_per_second else 0

    def monitor_stats(self):
        """
        | **@author:** Prathyush SP
        |
        :return - Monitor Statistics
        """
        return OrderedDict([
            ('total_memory (GB)', psutil.virtual_memory().total / 2 ** 30),
            ('memory_usage_per_second (MBps)', self.memory_usage_per_second),
            ('max_memory_usage (MB)', self.max_memory_usage)
        ])
