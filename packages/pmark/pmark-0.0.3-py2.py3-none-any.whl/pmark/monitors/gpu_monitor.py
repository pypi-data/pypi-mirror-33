# -*- coding: utf-8 -*-
"""
| **@created on:** 30/06/18,
| **@author:** prathyushsp,
| **@version:** v0.0.1
|
| **Description:**
| GPU Monitor Module
|
| **Sphinx Documentation Status:** --
|
..todo::
"""
__all__ = ['GPUMonitor']

from pmark.monitors.monitor import Monitor
import typing
import pmark.string_constants as constants
from collections import OrderedDict
from pmark.monitors.gpustat import get_gpu_stats


class GPUMonitor(Monitor):
    """
    | **@author:** Prathyush SP
    |
    | Description: This class is for monitoring the GPU usage
    """

    def __init__(self, pid: int, interval_in_secs: typing.Union[int, float] = 1):
        """
        | **@author:** Prathyush SP
        |
        | GPUMonitor initializer function
        :param pid: Process ID of the process that needs to be monitored
        :param interval: Interval at which the process needs to be monitored
        """
        Monitor.__init__(self, pid=pid, interval_in_secs=interval_in_secs,
                         monitor_type=constants.Monitors.Type.GpuMonitor)

        # Get the stats using nvidia-smi python wrapper
        stats = get_gpu_stats()
        self.monitor_disabled = True if stats == 'ERROR' else self.monitor_disabled
        if not self.monitor_disabled:
            self.number_gpus = len(stats)
            self.gpus = list(stats.keys())

            self.gpu_total_memory = {g: stats[g]['TotalMemory'] for g in self.gpus}
            self.gpu_power_limit = {g: stats[g]['PowerLimit'] for g in self.gpus}

            self.gpu_memory_usage_per_interval = {g: [] for g in self.gpus}
            self.gpu_utilization_per_interval = {g: [] for g in self.gpus}
            self.gpu_power_drawn_per_interval = {g: [] for g in self.gpus}
            self.gpu_graphics_clock_per_interval = {g: [] for g in self.gpus}
            self.gpu_sm_clock_per_interval = {g: [] for g in self.gpus}
            self.gpu_memory_clock_per_interval = {g: [] for g in self.gpus}
            self.gpu_temperature_per_interval = {g: [] for g in self.gpus}

            self.gpu_max_memory_usage = None
            self.gpu_max_utilization = None
            self.gpu_max_power_drawn = None
            self.gpu_max_graphics_clock = None
            self.gpu_max_sm_clock = None
            self.gpu_max_memory_clock = None
            self.gpu_max_temperature = None

    def monitor_running(self):
        """
        | **@author:** Prathyush SP
        |
        | Fetch statistics while monitoring the process
        :return:
        """
        stats = get_gpu_stats()
        for k, v in stats.items():
            assert k in self.gpus
            self.gpu_memory_usage_per_interval[k].append(v['UsedMemory'])
            self.gpu_utilization_per_interval[k].append(v['GPUUtilization'])
            self.gpu_power_drawn_per_interval[k].append(v['PowerDrawn'])
            self.gpu_graphics_clock_per_interval[k].append(v['GraphicsClock'])
            self.gpu_sm_clock_per_interval[k].append(v['SMClock'])
            self.gpu_memory_clock_per_interval[k].append(v['MemoryClock'])
            self.gpu_temperature_per_interval[k].append(v['GPUTemperature'])

    def monitor_stopped(self):
        """
        |**@author:** Prathyush SP
        |
        | Create the summary from the monitored statistics
        :return:
        """
        self.gpu_max_memory_usage = self._calc_max(stats=self.gpu_memory_usage_per_interval)
        self.gpu_max_utilization = self._calc_max(stats=self.gpu_utilization_per_interval)
        self.gpu_max_power_drawn = self._calc_max(stats=self.gpu_power_drawn_per_interval)
        self.gpu_max_graphics_clock = self._calc_max(stats=self.gpu_graphics_clock_per_interval)
        self.gpu_max_sm_clock = self._calc_max(stats=self.gpu_sm_clock_per_interval)
        self.gpu_max_memory_clock = self._calc_max(stats=self.gpu_memory_clock_per_interval)
        self.gpu_max_temperature = self._calc_max(stats=self.gpu_temperature_per_interval)

    def _calc_max(self, stats: dict):
        """
        | **@author:** Prathyush SP
        |
        | Calculates the max value of every list in a given dict
        :param stats: A dict containing lists of usage for all the GPUs
        :return:
        """
        max_dict = {}
        for g in self.gpus:
            max_dict[g] = None
            if len(stats[g]) > 0:
                max_dict[g] = max(stats[g])
        return max_dict

    def monitor_stats(self):
        """
        | **@author:** Prathyush SP
        |
        | Return the collected statistics in an ordered dict
        :return:
        """
        if self.monitor_disabled:
            return OrderedDict([('error', 'Monitor was disabled')])
        return OrderedDict([
            ('gpu_count', self.number_gpus),
            ('gpu_devices', self.gpus),
            ('gpu_total_memory (in MiB)', self.gpu_total_memory),
            ('gpu_power_limit (in Watt)', self.gpu_power_limit),
            ('gpu_memory_usage_per_interval (in MiB)', self.gpu_memory_usage_per_interval),
            ('gpu_utilization_per_interval (in %)', self.gpu_utilization_per_interval),
            ('gpu_power_drawn_per_interval (in Watt)', self.gpu_power_drawn_per_interval),
            ('gpu_graphics_clock_per_interval (in MHz)', self.gpu_graphics_clock_per_interval),
            ('gpu_sm_clock_per_interval (in MHz)', self.gpu_sm_clock_per_interval),
            ('gpu_memory_clock_per_interval (in MHz)', self.gpu_memory_clock_per_interval),
            ('gpu_temperature_per_interval (in degree C)', self.gpu_temperature_per_interval),
            ('gpu_max_memory_usage (in MiB)', self.gpu_max_memory_usage),
            ('gpu_max_utilization (in %)', self.gpu_max_utilization),
            ('gpu_max_power_drawn (in Watt)', self.gpu_max_power_drawn),
            ('gpu_max_graphics_clock (in MHz)', self.gpu_max_graphics_clock),
            ('gpu_max_sm_clock (in MHz)', self.gpu_max_sm_clock),
            ('gpu_max_memory_clock (in MHz)', self.gpu_max_memory_clock),
            ('gpu_max_temperature (in degree C)', self.gpu_max_temperature),
        ])
