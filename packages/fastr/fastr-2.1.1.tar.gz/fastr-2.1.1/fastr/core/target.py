# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The module containing the classes describing the targets.
"""

from abc import ABCMeta, abstractmethod
from collections import deque, namedtuple, Sequence
import datetime
import platform
import psutil
import time
import threading
import shellescape
import subprocess

import fastr
from fastr.core.baseplugin import Plugin
from fastr.core.pluginmanager import PluginSubManager
from fastr import exceptions

SystemUsageInfo = namedtuple('SystemUsageInfo', ['timestamp',
                                                 'cpu_percent',
                                                 'vmem',
                                                 'rmem',
                                                 'read_bytes',
                                                 'write_bytes'])


class ProcessUsageCollection(Sequence):
    # It has to be defined in module for pickling purposes
    usage_type = SystemUsageInfo

    def __init__(self):
        self.seconds_info = deque()
        self.minutes_info = []

    def __len__(self):
        return len(self.seconds_info) + len(self.minutes_info)

    def __getitem__(self, item):
        # First look in minutes, then in seconds
        if item < len(self.minutes_info):
            return self.minutes_info[item]._asdict()
        else:
            return self.seconds_info[item - len(self.minutes_info)]._asdict()

    def append(self, value):
        if not isinstance(value, self.usage_type):
            raise ValueError('Cannot add a non {}.usage_type'.format(type(self).__name__))

        self.seconds_info.append(value)

        if len(self.seconds_info) >= 120:
            self.aggregate(60)

    def aggregate(self, number_of_points):
        oldest_data = [self.seconds_info.popleft() for _ in range(number_of_points)]

        timestamp = oldest_data[-1].timestamp
        cpu_percent = sum(x.cpu_percent for x in oldest_data) / len(oldest_data)
        vmem = max(x.vmem for x in oldest_data)
        rmem = max(x.rmem for x in oldest_data)
        read_bytes = oldest_data[-1].read_bytes
        write_bytes = oldest_data[-1].write_bytes

        self.minutes_info.append(self.usage_type(timestamp=timestamp,
                                                 cpu_percent=cpu_percent,
                                                 vmem=vmem,
                                                 rmem=rmem,
                                                 read_bytes=read_bytes,
                                                 write_bytes=write_bytes))


class Target(Plugin):
    """
    The abstract base class for all targets. Execution with a target should
    follow the following pattern:

    >>> with Target() as target:
    ...     target.run_commmand(['sleep', '10'])

    The Target context operator will set the correct paths/initialization.
    Within the context command can be ran and when leaving the context the
    target reverts the state before.
    """
    __metaclass__ = ABCMeta

    # Monitor interval for profiling
    _MONITOR_INTERVAL = 1.0

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment where needed
        """

    @abstractmethod
    def run_command(self, command):
        pass

    @classmethod
    def test(cls):
        """
        Test the plugin, interfaces do not need to be tested on import
        """
        pass


class SubprocessBasedTarget(Target):
    """
    Abstract based class for targets which call the target via a subprocess.
    Supplies a call_subprocess which executes the command and profiles the
    resulting subprocess.
    """
    def call_subprocess(self, command):
        """
        Call a subprocess with logging/timing/profiling

        :param list command: the command to execute
        :return: execution info
        :rtype: dict
        """
        sysuse = ProcessUsageCollection()
        start_time = time.time()
        fastr.log.info('Calling command arguments: {}'.format(command))
        printable_command = []
        for item in command:
            printable_command.append(shellescape.quote(item))
        fastr.log.info('Calling command: "{}"'.format(' '.join(printable_command)))
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        except OSError as exception:
            if exception.errno == 2:
                raise exceptions.FastrExecutableNotFoundError(command[0])
            elif exception.errno == 13:
                # Permission denied
                raise exceptions.FastrNotExecutableError('Cannot execute {}, permission denied!'.format(command[0]))
            else:
                raise exception
        monitor_thread = threading.Thread(target=self.monitor_process, name='SubprocessMonitor', args=(process, sysuse))
        monitor_thread.daemon = True  # Make sure this Thread does not block exiting the script
        monitor_thread.start()
        stdout, stderr = process.communicate()
        return_code = process.poll()
        end_time = time.time()

        if monitor_thread.is_alive():
            monitor_thread.join(2 * self._MONITOR_INTERVAL)
            if monitor_thread.is_alive():
                fastr.log.warning('Ignoring unresponsive monitor thread!')

        return {'returncode': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'command': command,
                'resource_usage': list(sysuse),
                'time_elapsed': end_time - start_time}

    def monitor_process(self, process, resources):
        """
        Monitor a process and profile the cpu, memory and io use. Register the
        resource use every _MONITOR_INTERVAL seconds.

        :param subproces.Popen process: process to monitor
        :param ProcessUsageCollection resources: list to append measurements to
        """
        psproc = psutil.Process(process.pid)
        current_platform = platform.system().lower()

        # Loop initialization
        psproc.cpu_percent()  # Get rid of meaningless 0.0 at start
        last_timestamp = datetime.datetime.utcnow()

        while process.poll() is None:
            try:
                # The sleep duration is adapted to loop duration so aggregation will not cause
                # extended intervals
                sleep_duration = self._MONITOR_INTERVAL - (datetime.datetime.utcnow() - last_timestamp).total_seconds()
                sleep_duration = 0.0 if sleep_duration < 0.0 else sleep_duration
                time.sleep(sleep_duration)

                # Get process usage information
                memory_info = psproc.memory_info()

                if current_platform == 'darwin':
                    io_read = None
                    io_write = None
                else:
                    try:
                        io_info = psproc.io_counters()
                        io_read = io_info.read_bytes
                        io_write = io_info.write_bytes
                    except psutil.AccessDenied:
                        io_read = None
                        io_write = None

                last_timestamp = datetime.datetime.utcnow()
                usage = resources.usage_type(timestamp=last_timestamp.isoformat(),
                                             cpu_percent=psproc.cpu_percent(),
                                             vmem=memory_info.vms,
                                             rmem=memory_info.rss,
                                             read_bytes=io_read,
                                             write_bytes=io_write)

                resources.append(usage)

            except psutil.Error:
                # If the error occured because during the interval of meassuring the CPU use
                # the process stopped, we do not mind
                if process.poll() is None:
                    raise


class TargetManager(PluginSubManager):
    """
    Container holding all the ExecutionPlugins known to the Fastr system
    """

    def __init__(self):
        """
        Initialize a ExecutionPluginManager and load plugins.

        :param path: path to search for plugins
        :param recursive: flag for searching recursively
        :return: newly created ExecutionPluginManager
        """
        super(TargetManager, self).__init__(parent=fastr.plugin_manager,
                                            plugin_class=Target)


