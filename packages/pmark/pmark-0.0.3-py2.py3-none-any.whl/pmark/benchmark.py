# -*- coding: utf-8 -*-
"""
| **@created on:** 16/12/16,
| **@author:** Prathyush SP,
| **@version:** v0.0.1
|
| **Description:**
| Benchmark Module
|
| Sphinx Documentation Status:**
|
..todo::


Benchmark Statistics:
1.	Physical Memory Consumption - RAM	List[Float]	Max Physical Memory (RAM) consumed by the run in Mb/ GB - DONE
2.	Physical Memory Consumption - GPU	List[Float]	Max Physical Memory (GPU) consumed by the run in Mb/ GB
3.	Physical Processing Power Consumption	List[Float]	 Max Physical Power (CPU) consumed by the run in % - DONE
"""

import json
from collections import OrderedDict
from multiprocessing import Process
from multiprocessing.managers import BaseManager
import time
import os
import logging
from pmark.utils import generate_timestamp
from functools import wraps
import typing

logger = logging.getLogger(__name__)


# noinspection PyMissingOrEmptyDocstring
class BenchmarkStats(object):
    """
    | **@author:** Prathyush SP
    |
    | Benchmarking Statistics
    """

    def __init__(self, benchmark_name: str):  # pragma: no cover
        self.benchmark_name = benchmark_name
        self.function_name = None
        self.function_annotations = None
        self.total_elapsed_time = None
        self.monitor_statistics = OrderedDict()
        self.timestamp = generate_timestamp()
        self.internal_time = None

    def set_internal_time(self, t):
        self.internal_time = t

    def get_timestamp(self):
        return self.timestamp

    def get_benchmark_name(self):
        return self.benchmark_name

    def get_monitor_statistics(self):
        return self.monitor_statistics

    def set_monitor_statistics(self, status: OrderedDict):
        self.monitor_statistics = status

    def get_total_elapsed_time(self):
        return self.total_elapsed_time

    def set_total_elapsed_time(self, t):
        self.total_elapsed_time = t

    def get_function_name(self):
        return self.function_name

    def set_function_name(self, t):
        self.function_name = t

    def get_function_annotations(self):
        return self.function_annotations

    def set_function_annotations(self, t):
        self.function_annotations = t

    def info(self):  # pragma: no cover
        return OrderedDict([
            ('benchmark_name', self.benchmark_name),
            ('timestamp', self.timestamp),
            ('function_name', self.function_name),
            ('function_annotations', self.function_annotations),
            ('total_elapsed_time (secs)', self.total_elapsed_time),
            ('monitor_statistics', self.monitor_statistics),
            ('internal_time', self.internal_time)
        ])


class BenchmarkUtil(object):
    """
    | **@author:** Prathyush SP
    |
    | Benchmark Util - 
    | Performs Training and Inference Benchmarks
    """

    def __init__(self, name: str, stats_save_path: str,
                 monitors: typing.List = None, interval_in_secs: int = None):
        """

        :param name: Util Name
        :param stats_save_path: Stats save path
        :param monitors: List of Monitors
        :param interval_in_secs:
        """
        self.name = name
        self.deployed_monitors = monitors
        self.monitors = None
        self.benchmark_interval = interval_in_secs
        self.pid = None
        self.stats_save_path = stats_save_path
        os.system('mkdir -p ' + self.stats_save_path + '../graphs/')

    def _attach_monitors(self, pid: int):
        """
        | **@author:** Prathyush SP
        |
        | Attach Various Monitors and waits
        :param pid: Process Id
        """

        if self.deployed_monitors:
            # Initialize Monitors
            self.monitors = [
                monitor(pid=pid, interval=self.benchmark_interval) if isinstance(monitor, type) else monitor
                for monitor in self.deployed_monitors]

            # Start Monitors
            for monitor in self.monitors:
                monitor.start()

            # Wait for Monitors
            for monitor in self.monitors:
                monitor.join()

    def _collect_monitor_stats(self):
        """
        | **@author:** Prathyush SP
        |
        | Collect Monitor Statistics
        """
        if self.monitors:
            return OrderedDict([(monitor.monitor_type, monitor.monitor_stats()) for monitor in self.monitors])
        return None

    def monitor(self, f):
        """
        | **@author:** Prathyush SP
        |
        | Value Exception Decorator.
        :param f: Function
        :return: Function Return Parameter
        """

        # noinspection PyUnresolvedReferences
        @wraps(f)
        def wrapped(*args, **kwargs):
            start = time.time()
            print('Running Benchmark - Training . . .')
            BaseManager.register('BenchmarkStats', BenchmarkStats)
            manager = BaseManager()
            manager.start()
            b_stats = manager.BenchmarkStats(self.model_name)
            b_stats.set_function_name(f.__name__)
            b_stats.set_function_annotations(f.__annotations__)
            try:
                p = Process(target=f, args=())
                p.start()
                self.pid = p.pid
                self._attach_monitors(pid=p.pid)
                p.join()
                b_stats.set_monitor_statistics(self._collect_monitor_stats())
                b_stats.set_total_elapsed_time(time.time() - start)
                fname = self.stats_save_path + '/benchmark_{}_{}.json'.format(
                    b_stats.get_benchmark_name().replace(' ', '_'), b_stats.get_timestamp())
                b_stats.set_internal_time(json.load(open('/tmp/time.json'))['internal_time'])
                json.dump(b_stats.info(),
                          open(fname, 'w'), indent=2)
                print('Benchmark Util - Training completed successfully. Results stored at: {}'.format(fname))
            except ValueError as ve:
                logger.error('Value Error - {}'.format(ve))
                raise Exception('Value Error', ve)

        return wrapped

    def clean_up(self):
        """
        | **@author:** Prathyush SP
        |
        | Cleanup operations after benchmarking
        """
        pass  # pragma: no cover
