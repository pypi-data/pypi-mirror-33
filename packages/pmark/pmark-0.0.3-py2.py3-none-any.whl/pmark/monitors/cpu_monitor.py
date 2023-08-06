# -*- coding: utf-8 -*-
"""
| **@created on:** 30/06/18,
| **@author:** prathyushsp,
| **@version:** v0.0.1
|
| **Description:**
| CPU Monitor Module
|
| **Sphinx Documentation Status:** --
|
..todo::
"""

__all__ = ['CPUMonitor']

from pmark.monitors.monitor import Monitor
import typing
import pmark.string_constants as constants
from collections import OrderedDict
import psutil


class CPUMonitor(Monitor):
    """
    | **@author:** Prathyush SP
    |
    | CPU Monitor
    """

    def __init__(self, pid: int, interval_in_secs: typing.Union[int, float] = 1):
        """

        :param pid: Process ID
        :param interval_in_secs: Interval In Seconds
        """
        Monitor.__init__(self, pid=pid, interval_in_secs=interval_in_secs,
                         monitor_type=constants.Monitors.Type.CpuMonitor)
        self.cpu_usage_per_second = []
        self.max_cpu_usage = None

    def monitor_running(self):
        """
        | **@author:** Prathyush SP
        |
        | Initialize / Update monitor variables during runtime
        """
        self.cpu_usage_per_second.append(self.psutil_process.cpu_percent() / psutil.cpu_count())

    def monitor_stopped(self):
        """
        | **@author:** Prathyush SP
        |
        | Initialize / Update monitor variables on stop
        """
        self.max_cpu_usage = float(max(self.cpu_usage_per_second)) if self.cpu_usage_per_second else 0

    def monitor_stats(self):
        """
        | **@author:** Prathyush SP
        |
        :return - Monitor Statistics
        """
        return OrderedDict([
            ('cpu_cores', psutil.cpu_count(logical=False)),
            ('cpu_threads', psutil.cpu_count()),
            ('cpu_usage_per_second (%/s)', self.cpu_usage_per_second),
            ('max_cpu_usage (%)', self.max_cpu_usage)
        ])
