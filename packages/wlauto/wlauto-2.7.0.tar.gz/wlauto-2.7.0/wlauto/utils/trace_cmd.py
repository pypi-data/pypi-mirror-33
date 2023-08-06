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

import re
import logging
from itertools import chain

from wlauto.utils.misc import isiterable, memoized
from wlauto.utils.types import numeric


logger = logging.getLogger('trace-cmd')


# These markers can be injected into trace to identify the  "interesting"
# portion.
TRACE_MARKER_START = 'TRACE_MARKER_START'
TRACE_MARKER_STOP = 'TRACE_MARKER_STOP'


class TraceCmdEvent(object):
    """
    A single trace-cmd event. This will appear in the trace cmd report in the format ::

          <idle>-0     [000]  3284.126993: sched_rq_runnable_load: cpu=0 load=54
             |           |         |              |                |___________|
             |           |         |              |                      |
          thread        cpu    timestamp        name                    body

    """

    __slots__ = ['thread', 'reporting_cpu_id', 'timestamp', 'name', 'text', '_fields', '_parser']

    @property
    def fields(self):
        if self._fields is not None:
            return self._fields
        self._fields = {}

        if self._parser:
            try:
                self._parser(self, self.text)
            except Exception:  # pylint: disable=broad-except
                # unknown format assume user does not care or know how to
                # parse self.text
                pass
        return self._fields

    def __init__(self, thread, cpu_id, ts, name, body, parser=None):
        """
        parameters:

        :thread: thread which generated the event
        :cpu: cpu on which the event has occurred
        :ts: timestamp of the event
        :name: the name of the event
        :bodytext: a string with the rest of the event text
        :parser: optionally, a function that will parse bodytext to populate
                 this event's attributes

        The parser can be any callable that can be invoked with

            parser(event, text)

        Where ``event`` is this TraceCmdEvent instance, and ``text`` is the body text to be
        parsed. The parser should updated the passed event instance and not return anything
        (the return value will be ignored). Any exceptions raised by the parser will be silently
        ignored (note that this means that the event's attributes may be partially initialized).

        """
        self.thread = thread
        self.reporting_cpu_id = int(cpu_id)
        self.timestamp = numeric(ts)
        self.name = name
        self.text = body
        self._fields = None
        self._parser = parser

    def __getattr__(self, name):
        try:
            return self.fields[name]
        except KeyError:
            raise AttributeError(name)

    def __str__(self):
        return 'TE({} @ {})'.format(self.name, self.timestamp)

    __repr__ = __str__


class DroppedEventsEvent(object):

    __slots__ = ['thread', 'reporting_cpu_id', 'timestamp', 'name', 'text', 'fields']

    def __init__(self, cpu_id):
        self.thread = None
        self.reporting_cpu_id = None
        self.timestamp = None
        self.name = 'DROPPED EVENTS DETECTED'
        self.text = None
        self.fields = {'cpu_id': int(cpu_id)}

    def __getattr__(self, name):
        try:
            return self.fields[name]
        except KeyError:
            raise AttributeError(name)

    def __str__(self):
        return 'DROPPED_EVENTS_ON_CPU{}'.format(self.cpu_id)

    __repr__ = __str__


def try_convert_to_numeric(v):
    try:
        if isiterable(v):
            return map(numeric, v)
        else:
            return numeric(v)
    except ValueError:
        return v


def default_body_parser(event, text):
    """
    Default parser to attempt to use to parser body text for the event (i.e. after
    the "header" common to all events has been parsed). This assumes that the body is
    a whitespace-separated list of key=value pairs. The parser will attempt to convert
    the value into a numeric type, and failing that, keep it as string.

    """
    parts = [e.rsplit(' ', 1) for e in text.strip().split('=')]
    parts = [p.strip() for p in chain.from_iterable(parts)]
    if not len(parts) % 2:
        i = iter(parts)
        for k, v in zip(i, i):
            try:
                v = int(v)
            except ValueError:
                pass
            event._fields[k] = v


def regex_body_parser(regex, flags=0):
    """
    Creates an event body parser form the specified regular expression (could be an
    ``re.RegexObject``, or a string). The regular expression should contain some named
    groups, as those will be extracted as the event attributes (unnamed groups and the
    reset of the match will be ignored).

    If the specified regex is a string, it will be compiled, in which case ``flags`` may
    be provided for the resulting regex object (see ``re`` standard module documentation).
    If regex is a pre-compiled object, flags will be ignored.

    """
    if isinstance(regex, basestring):
        regex = re.compile(regex, flags)

    def regex_parser_func(event, text):
        match = regex.search(text)
        if match:
            for k, v in match.groupdict().iteritems():
                try:
                    event._fields[k] = int(v)
                except ValueError:
                    event._fields[k] = v

    return regex_parser_func


def sched_switch_parser(event, text):
    """
    Sched switch output may be presented in a couple of different formats. One is handled
    by a regex. The other format can *almost* be handled by the default parser, if it
    weren't for the ``==>`` that appears in the middle.
    """
    if text.count('=') == 2:  # old format
        regex = re.compile(
            r'(?P<prev_comm>\S.*):(?P<prev_pid>\d+) \[(?P<prev_prio>\d+)\] (?P<status>\S+)'
            r' ==> '
            r'(?P<next_comm>\S.*):(?P<next_pid>\d+) \[(?P<next_prio>\d+)\]'
        )
        parser_func = regex_body_parser(regex)
        return parser_func(event, text)
    else:  # there are more than two "=" -- new format
        return default_body_parser(event, text.replace('==>', ''))


def sched_stat_parser(event, text):
    """
    sched_stat_* events unclude the units, "[ns]", in an otherwise
    regular key=value sequence; so the units  need to be stripped out first.
    """
    return default_body_parser(event, text.replace(' [ns]', ''))


def sched_wakeup_parser(event, text):
    regex = re.compile(r'(?P<comm>\S+):(?P<pid>\d+) \[(?P<prio>\d+)\] success=(?P<success>\d) CPU:(?P<cpu>\d+)')
    parse_func = regex_body_parser(regex)
    return parse_func(event, text)


# Maps event onto the corresponding parser for its body text. A parser may be
# a callable with signature
#
#   parser(event, bodytext)
#
# a re.RegexObject, or a string (in which case it will be compiled into a
# regex). In case of a string/regex, its named groups will be used to populate
# the event's attributes.
EVENT_PARSER_MAP = {
    'sched_stat_blocked': sched_stat_parser,
    'sched_stat_iowait': sched_stat_parser,
    'sched_stat_runtime': sched_stat_parser,
    'sched_stat_sleep': sched_stat_parser,
    'sched_stat_wait': sched_stat_parser,
    'sched_switch': sched_switch_parser,
    'sched_wakeup': sched_wakeup_parser,
    'sched_wakeup_new': sched_wakeup_parser,
}

HEADER_REGEX = re.compile(r'^\s*(?:version|cpus)\s*=\s*([\d.]+)\s*$')

DROPPED_EVENTS_REGEX = re.compile(r'CPU:(?P<cpu_id>\d+) \[\d*\s*EVENTS DROPPED\]')

EMPTY_CPU_REGEX = re.compile(r'CPU \d+ is empty')


def split_trace_event_line(line):
    """
    Split a trace-cmd event line into the preamble (containing the task, cpu id
    and timestamp), the event name, and the event body. Each of these is
    delimited by a ': ' (optionally followed by more whitespace), however ': '
    may also appear in the body of the event and in the thread name. This
    attempts to identify the correct split by ensureing the there is a '['
    (used to mark the cpu id and not a valid character for a task name) in the
    peramble.

    """
    parts = line.split(': ')
    if len(parts) <= 3:
        return parts

    preamble = parts.pop(0)
    while '[' not in preamble:
        preamble += ': ' + parts.pop(0)
    event_name = parts.pop(0)
    return (preamble, event_name, ': '.join(parts))


class TraceCmdTrace(object):

    @property
    @memoized
    def has_start_marker(self):
        with open(self.file_path) as fh:
            for line in fh:
                if TRACE_MARKER_START in line:
                    return True
            return False

    def __init__(self, file_path, names=None, filter_markers=True):
        self.filter_markers = filter_markers
        self.file_path = file_path
        self.names = names or []

    def parse(self):  # pylint: disable=too-many-branches,too-many-locals
        """
        This is a generator for the trace event stream.

        """
        inside_marked_region = False
        filters = [re.compile('^{}$'.format(n)) for n in self.names or []]
        with open(self.file_path) as fh:
            for line in fh:
                # if processing trace markers, skip marker lines as well as all
                # lines outside marked region
                if self.filter_markers:
                    if not inside_marked_region:
                        if TRACE_MARKER_START in line:
                            inside_marked_region = True
                        continue
                    elif TRACE_MARKER_STOP in line:
                        break

                if 'EVENTS DROPPED' in line:
                    match = DROPPED_EVENTS_REGEX.search(line)
                    if match:
                        yield DroppedEventsEvent(match.group('cpu_id'))
                        continue

                if line.startswith('version') or line.startswith('cpus') or\
                        line.startswith('CPU:'):
                    matched = False
                    for rx in [HEADER_REGEX, EMPTY_CPU_REGEX]:
                        match = rx.search(line)
                        if match:
                            logger.debug(line.strip())
                            matched = True
                            break
                    if matched:
                        continue

                # <thread/cpu/timestamp>: <event name>: <event body>
                parts = split_trace_event_line(line)
                if len(parts) != 3:
                    continue

                event_name = parts[1].strip()

                if filters:
                    found = False
                    for f in filters:
                        if f.search(event_name):
                            found = True
                            break
                    if not found:
                        continue

                thread_string, rest = parts[0].rsplit(' [', 1)
                cpu_id, ts_string = rest.split('] ')
                body = parts[2].strip()

                body_parser = EVENT_PARSER_MAP.get(event_name, default_body_parser)
                if isinstance(body_parser, basestring) or isinstance(body_parser, re._pattern_type):  # pylint: disable=protected-access
                    body_parser = regex_body_parser(body_parser)

                yield TraceCmdEvent(
                    thread=thread_string.strip(),
                    cpu_id=cpu_id,
                    ts=ts_string.strip(),
                    name=event_name,
                    body=body,
                    parser=body_parser,
                )
            else:
                if self.filter_markers and inside_marked_region:
                    logger.warning('Did not encounter a stop marker in trace')
