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

from __future__ import division
import os
import sys
import csv
import re
import logging
from ctypes import c_int32
from collections import defaultdict
import argparse

from wlauto.utils.trace_cmd import TraceCmdTrace, TRACE_MARKER_START, TRACE_MARKER_STOP
from wlauto.exceptions import DeviceError


logger = logging.getLogger('power')

UNKNOWN_FREQUENCY = -1

INIT_CPU_FREQ_REGEX = re.compile(r'CPU (?P<cpu>\d+) FREQUENCY: (?P<freq>\d+) kHZ')
DEVLIB_CPU_FREQ_REGEX = re.compile(r'cpu_frequency(?:_devlib):\s+state=(?P<freq>\d+)\s+cpu_id=(?P<cpu>\d+)')


class CorePowerTransitionEvent(object):

    kind = 'transition'
    __slots__ = ['timestamp', 'cpu_id', 'frequency', 'idle_state']

    def __init__(self, timestamp, cpu_id, frequency=None, idle_state=None):
        if (frequency is None) == (idle_state is None):
            raise ValueError('Power transition must specify a frequency or an idle_state, but not both.')
        self.timestamp = timestamp
        self.cpu_id = cpu_id
        self.frequency = frequency
        self.idle_state = idle_state

    def __str__(self):
        return 'cpu {} @ {} -> freq: {} idle: {}'.format(self.cpu_id, self.timestamp,
                                                         self.frequency, self.idle_state)

    def __repr__(self):
        return 'CPTE(c:{} t:{} f:{} i:{})'.format(self.cpu_id, self.timestamp,
                                                  self.frequency, self.idle_state)


class CorePowerDroppedEvents(object):

    kind = 'dropped_events'
    __slots__ = ['cpu_id']

    def __init__(self, cpu_id):
        self.cpu_id = cpu_id

    def __str__(self):
        return 'DROPPED EVENTS on CPU{}'.format(self.cpu_id)

    __repr__ = __str__


class TraceMarkerEvent(object):

    kind = 'marker'
    __slots__ = ['name']

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'MARKER: {}'.format(self.name)


class CpuPowerState(object):

    __slots__ = ['frequency', 'idle_state']

    @property
    def is_idling(self):
        return self.idle_state is not None and self.idle_state >= 0

    @property
    def is_active(self):
        return self.idle_state == -1

    def __init__(self, frequency=None, idle_state=None):
        self.frequency = frequency
        self.idle_state = idle_state

    def __str__(self):
        return 'CP(f:{} i:{})'.format(self.frequency, self.idle_state)

    __repr__ = __str__


class SystemPowerState(object):

    __slots__ = ['timestamp', 'cpus']

    @property
    def num_cores(self):
        return len(self.cpus)

    def __init__(self, num_cores, no_idle=False):
        self.timestamp = None
        self.cpus = []
        idle_state = -1 if no_idle else None
        for _ in xrange(num_cores):
            self.cpus.append(CpuPowerState(idle_state=idle_state))

    def copy(self):
        new = SystemPowerState(self.num_cores)
        new.timestamp = self.timestamp
        for i, c in enumerate(self.cpus):
            new.cpus[i].frequency = c.frequency
            new.cpus[i].idle_state = c.idle_state
        return new

    def __str__(self):
        return 'SP(t:{} Cs:{})'.format(self.timestamp, self.cpus)

    __repr__ = __str__


class PowerStateProcessor(object):
    """
    This takes a stream of power transition events and yields a timeline stream
    of system power states.

    """

    @property
    def cpu_states(self):
        return self.power_state.cpus

    @property
    def current_time(self):
        return self.power_state.timestamp

    @current_time.setter
    def current_time(self, value):
        self.power_state.timestamp = value

    def __init__(self, core_clusters, num_idle_states,
                 first_cluster_state=sys.maxint, first_system_state=sys.maxint,
                 wait_for_start_marker=False, no_idle=False):
        self.power_state = SystemPowerState(len(core_clusters), no_idle=no_idle)
        self.requested_states = {}  # cpu_id -> requeseted state
        self.wait_for_start_marker = wait_for_start_marker
        self._saw_start_marker = False
        self._saw_stop_marker = False
        self.exceptions = []

        idle_state_domains = build_idle_domains(core_clusters,
                                                num_states=num_idle_states,
                                                first_cluster_state=first_cluster_state,
                                                first_system_state=first_system_state)
        # This tells us what other cpus we need to update when we see an idle
        # state transition event
        self.idle_related_cpus = defaultdict(list)  # (cpu, idle_state) --> relate_cpus_list
        for state_id, idle_state_domain in enumerate(idle_state_domains):
            for cpu_group in idle_state_domain:
                for cpu in cpu_group:
                    related = set(cpu_group) - set([cpu])
                    self.idle_related_cpus[(cpu, state_id)] = related

    def process(self, event_stream):
        for event in event_stream:
            try:
                next_state = self.update_power_state(event)
                if self._saw_start_marker or not self.wait_for_start_marker:
                    yield next_state
                if self._saw_stop_marker:
                    break
            except Exception as e:  # pylint: disable=broad-except
                self.exceptions.append(e)
        else:
            if self.wait_for_start_marker:
                logger.warning("Did not see a STOP marker in the trace")

    def update_power_state(self, event):
        """
        Update the tracked power state based on the specified event and
        return updated power state.

        """
        if event.kind == 'transition':
            self._process_transition(event)
        elif event.kind == 'dropped_events':
            self._process_dropped_events(event)
        elif event.kind == 'marker':
            if event.name == 'START':
                self._saw_start_marker = True
            elif event.name == 'STOP':
                self._saw_stop_marker = True
        else:
            raise ValueError('Unexpected event type: {}'.format(event.kind))
        return self.power_state.copy()

    def _process_transition(self, event):
        self.current_time = event.timestamp
        if event.idle_state is None:
            self.cpu_states[event.cpu_id].frequency = event.frequency
        else:
            if event.idle_state == -1:
                self._process_idle_exit(event)
            else:
                self._process_idle_entry(event)

    def _process_dropped_events(self, event):
        self.cpu_states[event.cpu_id].frequency = None
        old_idle_state = self.cpu_states[event.cpu_id].idle_state
        self.cpu_states[event.cpu_id].idle_state = None

        related_ids = self.idle_related_cpus[(event.cpu_id, old_idle_state)]
        for rid in related_ids:
            self.cpu_states[rid].idle_state = None

    def _process_idle_entry(self, event):
        if self.cpu_states[event.cpu_id].is_idling:
            raise ValueError('Got idle state entry event for an idling core: {}'.format(event))
        self.requested_states[event.cpu_id] = event.idle_state
        self._try_transition_to_idle_state(event.cpu_id, event.idle_state)

    def _process_idle_exit(self, event):
        if self.cpu_states[event.cpu_id].is_active:
            raise ValueError('Got idle state exit event for an active core: {}'.format(event))
        self.requested_states.pop(event.cpu_id, None)  # remove outstanding request if there is one
        old_state = self.cpu_states[event.cpu_id].idle_state
        self.cpu_states[event.cpu_id].idle_state = -1
        if self.cpu_states[event.cpu_id].frequency is None:
            self.cpu_states[event.cpu_id].frequency = UNKNOWN_FREQUENCY

        related_ids = self.idle_related_cpus[(event.cpu_id, old_state)]
        if old_state is not None:
            new_state = old_state - 1
            for rid in related_ids:
                if self.cpu_states[rid].idle_state > new_state:
                    self._try_transition_to_idle_state(rid, new_state)

    def _try_transition_to_idle_state(self, cpu_id, idle_state):
        related_ids = self.idle_related_cpus[(cpu_id, idle_state)]

        # Tristate: True - can transition, False - can't transition,
        #           None - unknown idle state on at least one related cpu
        transition_check = self._can_enter_state(related_ids, idle_state)

        if transition_check is None:
            # Unknown state on a related cpu means we're not sure whether we're
            # entering requested state or a shallower one
            self.cpu_states[cpu_id].idle_state = None
            return

        # Keep trying shallower states until all related
        while not self._can_enter_state(related_ids, idle_state):
            idle_state -= 1
            related_ids = self.idle_related_cpus[(cpu_id, idle_state)]

        self.cpu_states[cpu_id].idle_state = idle_state
        for rid in related_ids:
            self.cpu_states[rid].idle_state = idle_state

    def _can_enter_state(self, related_ids, state):
        """
        This is a tri-state check. Returns ``True`` if related cpu states allow transition
        into this state, ``False`` if related cpu states don't allow transition into this
        state, and ``None`` if at least one of the related cpus is in an unknown state
        (so the decision of whether a transition is possible cannot be made).

        """
        for rid in related_ids:
            rid_requested_state = self.requested_states.get(rid, None)
            rid_current_state = self.cpu_states[rid].idle_state
            if rid_current_state is None:
                return None
            if rid_current_state < state:
                if rid_requested_state is None or rid_requested_state < state:
                    return False
        return True


def stream_cpu_power_transitions(events):
    for event in events:
        if event.name == 'cpu_idle':
            state = c_int32(event.state).value
            yield CorePowerTransitionEvent(event.timestamp, event.cpu_id, idle_state=state)
        elif event.name == 'cpu_frequency':
            yield CorePowerTransitionEvent(event.timestamp, event.cpu_id, frequency=event.state)
        elif event.name == 'DROPPED EVENTS DETECTED':
            yield CorePowerDroppedEvents(event.cpu_id)
        elif event.name == 'print':
            if TRACE_MARKER_START in event.text:
                yield TraceMarkerEvent('START')
            elif TRACE_MARKER_STOP in event.text:
                yield TraceMarkerEvent('STOP')
            else:
                if 'cpu_frequency' in event.text:
                    match = DEVLIB_CPU_FREQ_REGEX.search(event.text)
                else:
                    match = INIT_CPU_FREQ_REGEX.search(event.text)
                if match:
                    yield CorePowerTransitionEvent(event.timestamp,
                                                   int(match.group('cpu')),
                                                   frequency=int(match.group('freq')))


def gather_core_states(system_state_stream, freq_dependent_idle_states=None):  # NOQA
    if freq_dependent_idle_states is None:
        freq_dependent_idle_states = [0]
    for system_state in system_state_stream:
        core_states = []
        for cpu in system_state.cpus:
            if cpu.idle_state == -1:
                core_states.append((-1, cpu.frequency))
            elif cpu.idle_state in freq_dependent_idle_states:
                if cpu.frequency is not None:
                    core_states.append((cpu.idle_state, cpu.frequency))
                else:
                    core_states.append((None, None))
            else:
                core_states.append((cpu.idle_state, None))
        yield (system_state.timestamp, core_states)


def record_state_transitions(reporter, stream):
    for event in stream:
        if event.kind == 'transition':
            reporter.record_transition(event)
        yield event


class PowerStateTransitions(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self._wfh = open(filepath, 'w')
        self.writer = csv.writer(self._wfh)
        headers = ['timestamp', 'cpu_id', 'frequency', 'idle_state']
        self.writer.writerow(headers)

    def update(self, timestamp, core_states):  # NOQA
        # Just recording transitions, not doing anything
        # with states.
        pass

    def record_transition(self, transition):
        row = [transition.timestamp, transition.cpu_id,
               transition.frequency, transition.idle_state]
        self.writer.writerow(row)

    def report(self):
        self._wfh.close()


class PowerStateTimeline(object):

    def __init__(self, filepath, core_names, idle_state_names):
        self.filepath = filepath
        self.idle_state_names = idle_state_names
        self._wfh = open(filepath, 'w')
        self.writer = csv.writer(self._wfh)
        if core_names:
            headers = ['ts'] + ['{} CPU{}'.format(c, i)
                                for i, c in enumerate(core_names)]
            self.writer.writerow(headers)

    def update(self, timestamp, core_states):  # NOQA
        row = [timestamp]
        for idle_state, frequency in core_states:
            if frequency is None:
                if idle_state is None or idle_state == -1:
                    row.append(None)
                else:
                    row.append(self.idle_state_names[idle_state])
            else:  # frequency is not None
                if idle_state == -1:
                    if frequency == UNKNOWN_FREQUENCY:
                        frequency = 'Running (Unknown Hz)'
                    row.append(frequency)
                elif idle_state is None:
                    row.append(None)
                else:
                    if frequency == UNKNOWN_FREQUENCY:
                        frequency = 'Unknown Hz'
                    row.append('{} ({})'.format(self.idle_state_names[idle_state],
                                                frequency))
        self.writer.writerow(row)

    def report(self):
        self._wfh.close()


class ParallelStats(object):

    def __init__(self, core_clusters, use_ratios=False):
        self.clusters = defaultdict(set)
        self.use_ratios = use_ratios
        for i, clust in enumerate(core_clusters):
            self.clusters[clust].add(i)
        self.clusters['all'] = set(range(len(core_clusters)))

        self.first_timestamp = None
        self.last_timestamp = None
        self.previous_states = None
        self.parallel_times = defaultdict(lambda: defaultdict(int))
        self.running_times = defaultdict(int)

    def update(self, timestamp, core_states):
        if self.last_timestamp is not None:
            delta = timestamp - self.last_timestamp
            active_cores = [i for i, c in enumerate(self.previous_states)
                            if c and c[0] == -1]
            for cluster, cluster_cores in self.clusters.iteritems():
                clust_active_cores = len(cluster_cores.intersection(active_cores))
                self.parallel_times[cluster][clust_active_cores] += delta
                if clust_active_cores:
                    self.running_times[cluster] += delta
        else:  # initial update
            self.first_timestamp = timestamp

        self.last_timestamp = timestamp
        self.previous_states = core_states

    def report(self):  # NOQA
        if self.last_timestamp is None:
            return None

        report = ParallelReport()
        total_time = self.last_timestamp - self.first_timestamp
        for cluster in sorted(self.parallel_times):
            running_time = self.running_times[cluster]
            for n in xrange(len(self.clusters[cluster]) + 1):
                time = self.parallel_times[cluster][n]
                time_pc = time / total_time
                if not self.use_ratios:
                    time_pc *= 100
                if n:
                    if running_time:
                        running_time_pc = time / running_time
                    else:
                        running_time_pc = 0
                    if not self.use_ratios:
                        running_time_pc *= 100
                else:
                    running_time_pc = 0
                precision = self.use_ratios and 3 or 1
                fmt = '{{:.{}f}}'.format(precision)
                report.add([cluster, n,
                            fmt.format(time),
                            fmt.format(time_pc),
                            fmt.format(running_time_pc),
                            ])
        return report


class ParallelReport(object):

    def __init__(self):
        self.values = []

    def add(self, value):
        self.values.append(value)

    def write(self, filepath):
        with open(filepath, 'w') as wfh:
            writer = csv.writer(wfh)
            writer.writerow(['cluster', 'number_of_cores', 'total_time', '%time', '%running_time'])
            writer.writerows(self.values)


class PowerStateStats(object):

    def __init__(self, core_names, idle_state_names=None, use_ratios=False):
        self.core_names = core_names
        self.idle_state_names = idle_state_names
        self.use_ratios = use_ratios
        self.first_timestamp = None
        self.last_timestamp = None
        self.previous_states = None
        self.cpu_states = defaultdict(lambda: defaultdict(int))

    def update(self, timestamp, core_states):  # NOQA
        if self.last_timestamp is not None:
            delta = timestamp - self.last_timestamp
            for cpu, (idle, freq) in enumerate(self.previous_states):
                if idle == -1 and freq is not None:
                    state = '{:07}KHz'.format(freq)
                elif freq:
                    if self.idle_state_names:
                        state = '{}-{:07}KHz'.format(self.idle_state_names[idle], freq)
                    else:
                        state = 'idle{}-{:07}KHz'.format(idle, freq)
                elif idle not in (None, -1):
                    if self.idle_state_names:
                        state = self.idle_state_names[idle]
                    else:
                        state = 'idle{}'.format(idle)
                else:
                    state = 'unkown'
                self.cpu_states[cpu][state] += delta
        else:  # initial update
            self.first_timestamp = timestamp

        self.last_timestamp = timestamp
        self.previous_states = core_states

    def report(self):
        if self.last_timestamp is None:
            return None
        total_time = self.last_timestamp - self.first_timestamp
        state_stats = defaultdict(lambda: [None] * len(self.core_names))

        for cpu, states in self.cpu_states.iteritems():
            for state in states:
                time = states[state]
                time_pc = time / total_time
                if not self.use_ratios:
                    time_pc *= 100
                state_stats[state][cpu] = time_pc

        precision = self.use_ratios and 3 or 1
        return PowerStateStatsReport(state_stats, self.core_names, precision)


class PowerStateStatsReport(object):

    def __init__(self, state_stats, core_names, precision=2):
        self.state_stats = state_stats
        self.core_names = core_names
        self.precision = precision

    def write(self, filepath):
        with open(filepath, 'w') as wfh:
            writer = csv.writer(wfh)
            headers = ['state'] + ['{} CPU{}'.format(c, i)
                                   for i, c in enumerate(self.core_names)]
            writer.writerow(headers)
            for state in sorted(self.state_stats):
                stats = self.state_stats[state]
                fmt = '{{:.{}f}}'.format(self.precision)
                writer.writerow([state] + [fmt.format(s if s is not None else 0)
                                           for s in stats])


class CpuUtilisationTimeline(object):

    def __init__(self, filepath, core_names, max_freq_list):
        self.filepath = filepath
        self._wfh = open(filepath, 'w')
        self.writer = csv.writer(self._wfh)
        if core_names:
            headers = ['ts'] + ['{} CPU{}'.format(c, i)
                                for i, c in enumerate(core_names)]
            self.writer.writerow(headers)
        self._max_freq_list = max_freq_list

    def update(self, timestamp, core_states):  # NOQA
        row = [timestamp]
        for core, [idle_state, frequency] in enumerate(core_states):
            if idle_state == -1:
                if frequency == UNKNOWN_FREQUENCY:
                    frequency = 0
            elif idle_state is None:
                frequency = 0
            else:
                frequency = 0
            if core < len(self._max_freq_list):
                frequency /= float(self._max_freq_list[core])
                row.append(frequency)
            else:
                logger.warning('Unable to detect max frequency for this core. Cannot log utilisation value')
        self.writer.writerow(row)

    def report(self):
        self._wfh.close()


def build_idle_domains(core_clusters,   # NOQA
                       num_states,
                       first_cluster_state=None,
                       first_system_state=None):
    """
    Returns a list of idle domain groups (one for each idle state). Each group is a
    list of domains, and a domain is a list of cpu ids for which that idle state is
    common. E.g.

        [[[0], [1], [2]], [[0, 1], [2]], [[0, 1, 2]]]

    This defines three idle states for a machine with three cores. The first idle state
    has three domains with one core in each domain; the second state has two domains,
    with cores 0 and 1 sharing one domain; the final state has only one domain shared
    by all cores.

    This mapping created based on the assumptions

    - The device is an SMP or a big.LITTLE-like system with cores in one or
      more clusters (for SMP systems, all cores are considered to be in a "cluster").
    - Idle domain correspend to either individual cores, individual custers, or
      the compute subsystem as a whole.
    - Cluster states are always deeper (higher index) than core states, and
      system states are always deeper than cluster states.

    parameters:

        :core_clusters: a list indicating cluster "ID" of the corresponing core, e.g.
                        ``[0, 0, 1]`` represents a three-core machines with cores 0
                        and 1 on cluster 0, and core 2 on cluster 1.
        :num_states: total number of idle states on a device.
        :first_cluster_state: the ID of the first idle state shared by all cores in a
                              cluster
        :first_system_state: the ID of the first idle state shared by all cores.

    """
    if first_cluster_state is None:
        first_cluster_state = sys.maxint
    if first_system_state is None:
        first_system_state = sys.maxint
    all_cpus = range(len(core_clusters))
    cluster_cpus = defaultdict(list)
    for cpu, cluster in enumerate(core_clusters):
        cluster_cpus[cluster].append(cpu)
    cluster_domains = [cluster_cpus[c] for c in sorted(cluster_cpus)]
    core_domains = [[c] for c in all_cpus]

    idle_state_domains = []
    for state_id in xrange(num_states):
        if state_id >= first_system_state:
            idle_state_domains.append([all_cpus])
        elif state_id >= first_cluster_state:
            idle_state_domains.append(cluster_domains)
        else:
            idle_state_domains.append(core_domains)

    return idle_state_domains


def report_power_stats(trace_file, idle_state_names, core_names, core_clusters,
                       num_idle_states, first_cluster_state=sys.maxint,
                       first_system_state=sys.maxint, use_ratios=False,
                       timeline_csv_file=None, cpu_utilisation=None,
                       max_freq_list=None, start_marker_handling='error',
                       transitions_csv_file=None, no_idle=False):
    # pylint: disable=too-many-locals,too-many-branches
    trace = TraceCmdTrace(trace_file,
                          filter_markers=False,
                          names=['cpu_idle', 'cpu_frequency', 'print'])

    wait_for_start_marker = True
    if start_marker_handling == "error" and not trace.has_start_marker:
        raise DeviceError("Start marker was not found in the trace")
    elif start_marker_handling == "try":
        wait_for_start_marker = trace.has_start_marker
        if not wait_for_start_marker:
            logger.warning("Did not see a START marker in the trace, "
                           "state residency and parallelism statistics may be inaccurate.")
    elif start_marker_handling == "ignore":
        wait_for_start_marker = False

    ps_processor = PowerStateProcessor(core_clusters,
                                       num_idle_states=num_idle_states,
                                       first_cluster_state=first_cluster_state,
                                       first_system_state=first_system_state,
                                       wait_for_start_marker=wait_for_start_marker,
                                       no_idle=no_idle)
    reporters = [
        ParallelStats(core_clusters, use_ratios),
        PowerStateStats(core_names, idle_state_names, use_ratios)
    ]
    if timeline_csv_file:
        reporters.append(PowerStateTimeline(timeline_csv_file,
                                            core_names, idle_state_names))
    if cpu_utilisation:
        if max_freq_list:
            reporters.append(CpuUtilisationTimeline(cpu_utilisation, core_names, max_freq_list))
        else:
            logger.warning('Maximum frequencies not found. Cannot normalise. Skipping CPU Utilisation Timeline')

    event_stream = trace.parse()
    transition_stream = stream_cpu_power_transitions(event_stream)
    if transitions_csv_file:
        trans_reporter = PowerStateTransitions(transitions_csv_file)
        reporters.append(trans_reporter)
        recorded_trans_stream = record_state_transitions(trans_reporter, transition_stream)
        power_state_stream = ps_processor.process(recorded_trans_stream)
    else:
        power_state_stream = ps_processor.process(transition_stream)
    core_state_stream = gather_core_states(power_state_stream)

    for timestamp, states in core_state_stream:
        for reporter in reporters:
            reporter.update(timestamp, states)

    if ps_processor.exceptions:
        logger.warning('There were errors while processing trace:')
        for e in ps_processor.exceptions:
            logger.warning(str(e))

    reports = []
    for reporter in reporters:
        report = reporter.report()
        reports.append(report)
    return reports


def main():
    # pylint: disable=unbalanced-tuple-unpacking
    logging.basicConfig(level=logging.INFO)
    args = parse_arguments()

    reports = report_power_stats(
        trace_file=args.infile,
        idle_state_names=args.idle_state_names,
        core_names=args.core_names,
        core_clusters=args.core_clusters,
        num_idle_states=args.num_idle_states,
        first_cluster_state=args.first_cluster_state,
        first_system_state=args.first_system_state,
        use_ratios=args.ratios,
        timeline_csv_file=args.timeline_file,
        cpu_utilisation=args.cpu_utilisation,
        max_freq_list=args.max_freq_list,
        start_marker_handling=args.start_marker_handling,
        transitions_csv_file=args.transitions_file,
        no_idle=args.no_idle,
    )

    parallel_report = reports.pop(0)
    powerstate_report = reports.pop(0)

    parallel_report.write(os.path.join(args.output_directory, 'parallel.csv'))
    powerstate_report.write(os.path.join(args.output_directory, 'cpustate.csv'))


class SplitListAction(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError('nargs not allowed')
        super(SplitListAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [v.strip() for v in values.split(',')])


def parse_arguments():  # NOQA
    parser = argparse.ArgumentParser(description="""
                                     Produce CPU power activity statistics reports from
                                     power trace.
                                     """)
    parser.add_argument('infile', metavar='TRACEFILE', help='''
                        Path to the trace file to parse. This must be in the format generated
                        by "trace-cmd report" command.
                        ''')
    parser.add_argument('-d', '--output-directory', default='.',
                        help='''
                        Output directory where reports will be placed.
                        ''')
    parser.add_argument('-c', '--core-names', action=SplitListAction,
                        help='''
                        Comma-separated list of core names for the device on which the trace
                        was collected.
                        ''')
    parser.add_argument('-C', '--core-clusters', action=SplitListAction, default=[],
                        help='''
                        Comma-separated list of core cluster IDs for the device on which the
                        trace was collected. If not specified, this will be generated from
                        core names on the assumption that all cores with the same name are on the
                        same cluster.
                        ''')
    parser.add_argument('-i', '--idle-state-names', action=SplitListAction,
                        help='''
                        Comma-separated list of idle state names. The number of names must match
                        --num-idle-states if that was explicitly specified.
                        ''')
    parser.add_argument('-n', '--num-idle-states', type=int,
                        help='''
                        number of  idle states on the device
                        ''')
    parser.add_argument('-q', '--first-cluster-state', type=int,
                        help='''
                        ID of the first cluster state. Must be < --num-idle-states.
                        ''')
    parser.add_argument('-s', '--first-system-state', type=int,
                        help='''
                        ID of the first system state. Must be < --numb-idle-states, and
                        > --first-cluster-state.
                        ''')
    parser.add_argument('-R', '--ratios', action='store_true',
                        help='''
                        By default proportional values will be reported as percentages, if this
                        flag is enabled, they will be reported as ratios instead.
                        ''')
    parser.add_argument('-t', '--timeline-file', metavar='FILE',
                        help='''
                        A timeline of core power states will be written to the specified file in
                        CSV format.
                        ''')
    parser.add_argument('-T', '--transitions-file', metavar='FILE',
                        help='''
                        A timeline of core power state transitions will be
                        written to the specified file in CSV format.
                        ''')
    parser.add_argument('-u', '--cpu-utilisation', metavar='FILE',
                        help='''
                        A timeline of cpu(s) utilisation will be written to the specified file in
                        CSV format.
                        ''')
    parser.add_argument('-m', '--max-freq-list', action=SplitListAction, default=[],
                        help='''
                        Comma-separated list of core maximum frequencies for the device on which
                        the trace was collected.
                        Only required if --cpu-utilisation is set.
                        This is used to normalise the frequencies to obtain percentage utilisation.
                        ''')
    parser.add_argument('-M', '--start-marker-handling', metavar='HANDLING', default="try",
                        choices=["error", "try", "ignore"],
                        help='''
                        The trace-cmd instrument inserts a marker into the trace to indicate the beginning
                        of workload execution. In some cases, this marker may be missing in the final
                        output (e.g. due to trace buffer overrun). This parameter specifies how a missing
                        start marker will be handled:

                         ignore:  The start marker will be ignored. All events in the trace will be used.
                         error:   An error will be raised if the start marker is not found in the trace.
                         try:     If the start marker is not found, all events in the trace will be used.
                        ''')
    parser.add_argument('-N', '--no-idle', action='store_true',
                        help='''
                        Assume that cpuidle is not present or disabled on the system, and therefore that the
                        initial state of the cores is that they are running. This flag is necessary because
                        the processor assumes the cores are in an unknown state until it sees the first idle
                        transition, which will never come if cpuidle is absent.
                        ''')

    args = parser.parse_args()

    if not args.core_names:
        raise ValueError('core names must be specified using -c or --core-names')
    if not args.core_clusters:
        logger.debug('core clusters not specified, inferring from core names')
        core_cluster_map = {}
        core_clusters = []
        current_cluster = 0
        for cn in args.core_names:
            if cn not in core_cluster_map:
                core_cluster_map[cn] = current_cluster
                current_cluster += 1
            core_clusters.append(core_cluster_map[cn])
        args.core_clusters = core_clusters
    if not args.num_idle_states and args.idle_state_names:
        args.num_idle_states = len(args.idle_state_names)
    elif args.num_idle_states and not args.idle_state_names:
        args.idle_state_names = ['idle{}'.format(i) for i in xrange(args.num_idle_states)]
    elif args.num_idle_states and args.idle_state_names:
        if len(args.idle_state_names) != args.num_idle_states:
            raise ValueError('Number of idle state names does not match --num-idle-states')
    else:
        raise ValueError('Either --num-idle-states or --idle-state-names must be specified')

    if not args.first_cluster_state and len(set(args.core_clusters)) > 1:
        if args.first_system_state:
            logger.debug('First cluster idle state not specified; state previous to first system state')
            args.first_cluster_state = args.first_system_state - 1
        else:
            logger.debug('First cluster idle state not specified; assuming last available state')
            args.first_cluster_state = args.num_idle_states - 1

    return args

if __name__ == '__main__':
    main()
