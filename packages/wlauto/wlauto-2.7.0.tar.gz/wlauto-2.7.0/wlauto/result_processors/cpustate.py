#    Copyright 2015 ARM Limited
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
#

import os
import csv
from collections import OrderedDict

from wlauto import ResultProcessor, Parameter
from wlauto.core import signal
from wlauto.exceptions import ConfigError, DeviceError
from wlauto.instrumentation import instrument_is_installed
from wlauto.utils.power import report_power_stats
from wlauto.utils.misc import unique


class CpuStatesProcessor(ResultProcessor):

    name = 'cpustates'
    description = '''
    Process power ftrace to produce CPU state and parallelism stats.

    Parses trace-cmd output to extract power events and uses those to generate
    statistics about parallelism and frequency/idle core residency.

    .. note:: trace-cmd instrument must be enabled and configured to collect
              at least ``power:cpu_idle`` and ``power:cpu_frequency`` events.
              Reporting should also be enabled (it is by default) as
              ``cpustate`` parses the text version of the trace.
              Finally, the device should have ``cpuidle`` module installed.

    This generates two reports for the run:

    *parallel.csv*

    Shows what percentage of time was spent with N cores active (for N
    from 0 to the total number of cores), for a cluster or for a system as
    a whole. It contain the following columns:

        :workload: The workload label
        :iteration: iteration that was run
        :cluster: The cluster for which statics are reported. The value of
                  ``"all"`` indicates that this row reports statistics for
                  the whole system.
        :number_of_cores: number of cores active. ``0`` indicates the cluster
                          was idle.
        :total_time: Total time spent in this state during workload execution
        :%time: Percentage of total workload execution time spent in this state
        :%running_time: Percentage of the time the cluster was active (i.e.
                        ignoring time the cluster was idling) spent in this
                        state.

    *cpustate.csv*

    Shows percentage of the time a core spent in a particular power state. The first
    column names the state is followed by a column for each core. Power states include
    available DVFS frequencies (for heterogeneous systems, this is the union of
    frequencies supported by different core types) and idle states. Some shallow
    states (e.g. ARM WFI) will consume different amount of power depending on the
    current OPP. For such states, there will be an entry for each opp. ``"unknown"``
    indicates the percentage of time for which a state could not be established from the
    trace. This is usually due to core state being unknown at the beginning of the trace,
    but may also be caused by dropped events in the middle of the trace.

    '''

    parameters = [
        Parameter('first_cluster_state', kind=int, default=2,
                  description="""
                  The first idle state which is common to a cluster.
                  """),
        Parameter('first_system_state', kind=int, default=3,
                  description="""
                  The first idle state which is common to all cores.
                  """),
        Parameter('write_iteration_reports', kind=bool, default=False,
                  description="""
                  By default, this instrument will generate reports for the entire run
                  in the overall output directory. Enabling this option will, in addition,
                  create reports in each iteration's output directory. The formats of these
                  reports will be similar to the overall report, except they won't mention
                  the workload name or iteration number (as that is implied by their location).
                  """),
        Parameter('use_ratios', kind=bool, default=False,
                  description="""
                  By default proportional values will be reported as percentages, if this
                  flag is enabled, they will be reported as ratios instead.
                  """),
        Parameter('create_timeline', kind=bool, default=True,
                  description="""
                  Create a CSV with the timeline of core power states over the course of the run
                  as well as the usual stats reports.
                  """),
        Parameter('create_utilization_timeline', kind=bool, default=False,
                  description="""
                  Create a CSV with the timeline of cpu(s) utilisation over the course of the run
                  as well as the usual stats reports.
                  The values generated are floating point numbers, normalised based on the maximum
                  frequency of the cluster.
                  """),
        Parameter('start_marker_handling', kind=str, default="try",
                  allowed_values=['ignore', 'try', 'error'],
                  description="""

                  The trace-cmd instrument inserts a marker into the trace to indicate the beginning
                  of workload execution. In some cases, this marker may be missing in the final
                  output (e.g. due to trace buffer overrun). This parameter specifies how a missing
                  start marker will be handled:

                  :`ignore`: The start marker will be ignored. All events in the trace will be used.
                  :`error`: An error will be raised if the start marker is not found in the trace.
                  :`try`: If the start marker is not found, all events in the trace will be used.
                  """),
        Parameter('no_idle', kind=bool, default=False,
                  description="""
                  Indicate that there will be no idle transitions in the trace. By default, a core
                  will be reported as being in an "unknown" state until the first idle transtion for
                  that core. Normally, this is not an issue, as cores are "nudged" as part of the setup
                  to ensure that there is an idle transtion before the meassured region. However, if all
                  idle states for the core have been disabled, or if the kernel does not have cpuidle,
                  the nudge will not result in an idle transition, which would cause the cores to be
                  reported to be in "unknown" state for the entire execution.

                  If this parameter is set to ``True``, the processor will assuming that cores are
                  running prior to the begining of the issue, and they will leave unknown state on
                  the first frequency transition.
                  """)
    ]

    def validate(self):
        if not instrument_is_installed('trace-cmd'):
            message = '''
            {} requires "trace-cmd" instrument to be installed and the collection of at
            least "power:cpu_frequency" and "power:cpu_idle" events to be enabled during worklad
            execution.
            '''
            raise ConfigError(message.format(self.name).strip())

    def initialize(self, context):
        # pylint: disable=attribute-defined-outside-init
        device = context.device
        for modname in ['cpuidle', 'cpufreq']:
            if not device.has(modname):
                message = 'Device does not appear to have {} capability; is the right module installed?'
                raise ConfigError(message.format(modname))
        if not device.core_names:
            message = '{} requires"core_names" and "core_clusters" to be specified for the device.'
            raise ConfigError(message.format(self.name))
        self.core_names = device.core_names
        self.core_clusters = device.core_clusters
        idle_states = {s.id: s.desc for s in device.get_cpuidle_states()}
        self.idle_state_names = [idle_states[i] for i in sorted(idle_states.keys())]
        self.num_idle_states = len(self.idle_state_names)
        self.iteration_reports = OrderedDict()
        self.max_freq_list = []
        # priority -19: just higher than the slow_start of instrumentation
        signal.connect(self.set_initial_state, signal.BEFORE_WORKLOAD_EXECUTION, priority=-19)

    def set_initial_state(self, context):
        # TODO: this does not play well with hotplug but leaving as-is, as this will be changed with
        # the devilib port anyway.
        # Write initial frequencies into the trace.
        # NOTE: this assumes per-cluster DVFS, that is valid for devices that
        # currently exist. This will need to be updated for per-CPU DFS.
        # pylint: disable=attribute-defined-outside-init
        self.logger.debug('Writing initial frequencies into trace...')
        device = context.device
        cluster_freqs = {}
        cluster_max_freqs = {}
        self.max_freq_list = []
        for c in unique(device.core_clusters):
            try:
                cluster_freqs[c] = device.get_cluster_cur_frequency(c)
                cluster_max_freqs[c] = device.get_cluster_max_frequency(c)
            except ValueError:
                cluster_freqs[c] = None
                cluster_max_freqs[c] = None
        for i, c in enumerate(device.core_clusters):
            self.max_freq_list.append(cluster_max_freqs[c])
            entry = 'CPU {} FREQUENCY: {} kHZ'.format(i, cluster_freqs[c])
            device.set_sysfile_value('/sys/kernel/debug/tracing/trace_marker',
                                     entry, verify=False)

        # Nudge each cpu to force idle state transitions in the trace
        self.logger.debug('Nudging all cores awake...')
        for i in xrange(len(device.core_names)):
            command = device.busybox + ' taskset 0x{:x} {}'
            try:
                device.execute(command.format(1 << i, 'ls'))
            except DeviceError:
                self.logger.warning("Failed to nudge CPU %s, has it been hot plugged out?", i)

    def process_iteration_result(self, result, context):
        trace = context.get_artifact('txttrace')
        if not trace:
            self.logger.debug('Text trace does not appear to have been generated; skipping this iteration.')
            return
        self.logger.debug('Generating power state reports from trace...')
        if self.create_timeline:
            timeline_csv_file = os.path.join(context.output_directory, 'power_states.csv')
        else:
            timeline_csv_file = None
        if self.create_utilization_timeline:
            cpu_utilisation = os.path.join(context.output_directory, 'cpu_utilisation.csv')
        else:
            cpu_utilisation = None

        reports = report_power_stats(  # pylint: disable=unbalanced-tuple-unpacking
            trace_file=trace.path,
            idle_state_names=self.idle_state_names,
            core_names=self.core_names,
            core_clusters=self.core_clusters,
            num_idle_states=self.num_idle_states,
            first_cluster_state=self.first_cluster_state,
            first_system_state=self.first_system_state,
            use_ratios=self.use_ratios,
            timeline_csv_file=timeline_csv_file,
            cpu_utilisation=cpu_utilisation,
            max_freq_list=self.max_freq_list,
            start_marker_handling=self.start_marker_handling,
            no_idle=self.no_idle,
        )
        parallel_report = reports.pop(0)
        powerstate_report = reports.pop(0)
        if parallel_report is None:
            self.logger.warning('No power state reports generated; are power '
                                'events enabled in the trace?')
            return
        else:
            self.logger.debug('Reports generated.')

        iteration_id = (context.spec.id, context.spec.label, context.current_iteration)
        self.iteration_reports[iteration_id] = (parallel_report, powerstate_report)
        if self.write_iteration_reports:
            self.logger.debug('Writing iteration reports')
            parallel_report.write(os.path.join(context.output_directory, 'parallel.csv'))
            powerstate_report.write(os.path.join(context.output_directory, 'cpustates.csv'))

    def process_run_result(self, result, context):  # pylint: disable=too-many-locals
        if not self.iteration_reports:
            self.logger.warning('No power state reports generated.')
            return

        parallel_rows = []
        powerstate_rows = []
        for iteration_id, reports in self.iteration_reports.iteritems():
            spec_id, workload, iteration = iteration_id
            parallel_report, powerstate_report = reports
            for record in parallel_report.values:
                parallel_rows.append([spec_id, workload, iteration] + record)
            for state in sorted(powerstate_report.state_stats):
                stats = powerstate_report.state_stats[state]
                powerstate_rows.append([spec_id, workload, iteration, state] +
                                       ['{:.3f}'.format(s if s is not None else 0)
                                           for s in stats])

        with open(os.path.join(context.output_directory, 'parallel.csv'), 'w') as wfh:
            writer = csv.writer(wfh)
            writer.writerow(['id', 'workload', 'iteration', 'cluster',
                             'number_of_cores', 'total_time',
                             '%time', '%running_time'])
            writer.writerows(parallel_rows)

        with open(os.path.join(context.output_directory, 'cpustate.csv'), 'w') as wfh:
            writer = csv.writer(wfh)
            headers = ['id', 'workload', 'iteration', 'state']
            headers += ['{} CPU{}'.format(c, i)
                        for i, c in enumerate(powerstate_report.core_names)]
            writer.writerow(headers)
            writer.writerows(powerstate_rows)
