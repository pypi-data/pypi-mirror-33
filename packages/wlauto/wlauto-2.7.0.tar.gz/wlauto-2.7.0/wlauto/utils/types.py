#    Copyright 2014-2015 ARM Limited
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


"""
Routines for doing various type conversions. These usually embody some higher-level
semantics than are present in standard Python types (e.g. ``boolean`` will convert the
string ``"false"`` to ``False``, where as non-empty strings are usually considered to be
``True``).

A lot of these are intened to stpecify type conversions declaratively in place like
``Parameter``'s ``kind`` argument. These are basically "hacks" around the fact that Python
is not the best language to use for configuration.

"""
import os
import re
import math
import shlex
from collections import defaultdict
from urllib import quote, unquote

from wlauto.utils.misc import isiterable, to_identifier


def identifier(text):
    """Converts text to a valid Python identifier by replacing all
    whitespace and punctuation."""
    return to_identifier(text)


def boolean(value):
    """
    Returns bool represented by the value. This is different from
    calling the builtin bool() in that it will interpret string representations.
    e.g. boolean('0') and boolean('false') will both yield False.

    """
    false_strings = ['', '0', 'n', 'no', 'off']
    if isinstance(value, basestring):
        value = value.lower()
        if value in false_strings or 'false'.startswith(value):
            return False
    return bool(value)


def integer(value):
    """Handles conversions for string respresentations of binary, octal and hex."""
    if isinstance(value, basestring):
        return int(value, 0)
    else:
        return int(value)


def numeric(value):
    """
    Returns the value as number (int if possible, or float otherwise), or
    raises ``ValueError`` if the specified ``value`` does not have a straight
    forward numeric conversion.

    """
    if isinstance(value, int):
        return value
    try:
        fvalue = float(value)
    except ValueError:
        raise ValueError('Not numeric: {}'.format(value))
    if not math.isnan(fvalue) and not math.isinf(fvalue):
        ivalue = int(fvalue)
        if ivalue == fvalue:  # yeah, yeah, I know. Whatever. This is best-effort.
            return ivalue
    return fvalue

def file_path(value):
    """Handles expansion of paths containing '~'"""
    return os.path.expanduser(value)

def list_of_strs(value):
    """
    Value must be iterable. All elements will be converted to strings.

    """
    if not isiterable(value):
        raise ValueError(value)
    return map(str, value)

list_of_strings = list_of_strs


def list_of_ints(value):
    """
    Value must be iterable. All elements will be converted to ``int``\ s.

    """
    if not isiterable(value):
        raise ValueError(value)
    return map(int, value)

list_of_integers = list_of_ints


def list_of_numbers(value):
    """
    Value must be iterable. All elements will be converted to numbers (either ``ints`` or
    ``float``\ s depending on the elements).
    """
    if not isiterable(value):
        raise ValueError(value)
    return map(numeric, value)


def list_of_bools(value, interpret_strings=True):
    """
    Value must be iterable. All elements will be converted to ``bool``\ s.

    .. note:: By default, ``boolean()`` conversion function will be used, which means that
              strings like ``"0"`` or ``"false"`` will be interpreted as ``False``. If this
              is undesirable, set ``interpret_strings`` to ``False``.

    """
    if not isiterable(value):
        raise ValueError(value)
    if interpret_strings:
        return map(boolean, value)
    else:
        return map(bool, value)


def list_of(type_):
    """Generates a "list of" callable for the specified type. The callable
    attempts to convert all elements in the passed value to the specifed
    ``type_``, raising ``ValueError`` on error."""
    def __init__(self, values):
        list.__init__(self, map(type_, values))

    def append(self, value):
        list.append(self, type_(value))

    def extend(self, other):
        list.extend(self, map(type_, other))

    def __setitem__(self, idx, value):
        list.__setitem__(self, idx, type_(value))

    return type('list_of_{}s'.format(type_.__name__),
                (list, ), {
                    "__init__": __init__,
                    "__setitem__": __setitem__,
                    "append": append,
                    "extend": extend,
    })


def list_or_string(value):
    """
    Converts the value into a list of strings. If the value is not iterable,
    a one-element list with stringified value will be returned.

    """
    if isinstance(value, basestring):
        return [value]
    else:
        try:
            return map(str, value)
        except ValueError:
            return [str(value)]


def list_or_caseless_string(value):
    """
    Converts the value into a list of ``caseless_string``'s. If the value is not iterable
    a one-element list with stringified value will be returned.

    """
    if isinstance(value, basestring):
        return [caseless_string(value)]
    else:
        try:
            return map(caseless_string, value)
        except ValueError:
            return [caseless_string(value)]


def list_or(type_):
    """
    Generator for "list or" types. These take either a single value or a list values
    and return a list of the specfied ``type_`` performing the conversion on the value
    (if a single value is specified) or each of the elemented of the specified list.

    """
    list_type = list_of(type_)

    class list_or_type(list_type):
        def __init__(self, value):
            # pylint: disable=non-parent-init-called,super-init-not-called
            if isiterable(value):
                list_type.__init__(self, value)
            else:
                list_type.__init__(self, [value])
    return list_or_type


list_or_integer = list_or(integer)
list_or_number = list_or(numeric)
list_or_bool = list_or(boolean)


regex_type = type(re.compile(''))


def regex(value):
    """
    Regular expression. If value is a string, it will be complied with no flags. If you
    want to specify flags, value must be precompiled.

    """
    if isinstance(value, regex_type):
        return value
    else:
        return re.compile(value)


__counters = defaultdict(int)


def reset_counter(name=None):
    __counters[name] = 0


def counter(name=None):
    """
    An auto incremeting value (kind of like an AUTO INCREMENT field in SQL).
    Optionally, the name of the counter to be used is specified (each counter
    increments separately).

    Counts start at 1, not 0.

    """
    __counters[name] += 1
    value = __counters[name]
    return value


class caseless_string(str):
    """
    Just like built-in Python string except case-insensitive on comparisons. However, the
    case is preserved otherwise.

    """

    def __eq__(self, other):
        if isinstance(other, basestring):
            other = other.lower()
        return self.lower() == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        if isinstance(basestring, other):
            other = other.lower()
        return cmp(self.lower(), other)

    def format(self, *args, **kwargs):
        return caseless_string(super(caseless_string, self).format(*args, **kwargs))


class arguments(list):
    """
    Represents command line arguments to be passed to a program.

    """

    def __init__(self, value=None):
        if isiterable(value):
            super(arguments, self).__init__(map(str, value))
        elif isinstance(value, basestring):
            posix = os.name != 'nt'
            super(arguments, self).__init__(shlex.split(value, posix=posix))
        elif value is None:
            super(arguments, self).__init__()
        else:
            super(arguments, self).__init__([str(value)])

    def append(self, value):
        return super(arguments, self).append(str(value))

    def extend(self, values):
        return super(arguments, self).extend(map(str, values))

    def __str__(self):
        return ' '.join(self)


class range_dict(dict):
    """
    This dict allows you to specify mappings with a range.

    If a key is not in the dict it will search downward until
    the next key and return its value. E.g:

    If:
        a[5] = "Hello"
        a[10] = "There"

    Then:
        a[2] == None
        a[7] == "Hello"
        a[999] == "There"

    """
    def __getitem__(self, i):
        key = int(i)
        while key not in self and key > 0:
            key -= 1
        if key <= 0:
            raise KeyError(i)
        return dict.__getitem__(self, key)

    def __setitem__(self, i, v):
        i = int(i)
        super(range_dict, self).__setitem__(i, v)


class ParameterDict(dict):
    """
    A dict-like object that automatically encodes various types into a url safe string,
    and enforces a single type for the contents in a list.
    Each value is first prefixed with 2 letters to preserve type when encoding to a string.
    The format used is "value_type, value_dimension" e.g a 'list of floats' would become 'fl'.
    """

    # Function to determine the appropriate prefix based on the parameters type
    @staticmethod
    def _get_prefix(obj):
        if isinstance(obj, basestring):
            prefix = 's'
        elif isinstance(obj, float):
            prefix = 'f'
        elif isinstance(obj, long):
            prefix = 'd'
        elif isinstance(obj, bool):
            prefix = 'b'
        elif isinstance(obj, int):
            prefix = 'i'
        elif obj is None:
            prefix = 'n'
        else:
            raise ValueError('Unable to encode {} {}'.format(obj, type(obj)))
        return prefix

    # Function to add prefix and urlencode a provided parameter.
    @staticmethod
    def _encode(obj):
        if isinstance(obj, list):
            t = type(obj[0])
            prefix = ParameterDict._get_prefix(obj[0]) + 'l'
            for item in obj:
                if not isinstance(item, t):
                    msg = 'Lists must only contain a single type, contains {} and {}'
                    raise ValueError(msg.format(t, type(item)))
            obj = '0newelement0'.join(str(x) for x in obj)
        else:
            prefix = ParameterDict._get_prefix(obj) + 's'
        return quote(prefix + str(obj))

    # Function to decode a string and return a value of the original parameter type.
    # pylint: disable=too-many-return-statements
    @staticmethod
    def _decode(string):
        value_type = string[:1]
        value_dimension = string[1:2]
        value = unquote(string[2:])
        if value_dimension == 's':
            if value_type == 's':
                return str(value)
            elif value_type == 'b':
                return boolean(value)
            elif value_type == 'd':
                return long(value)
            elif value_type == 'f':
                return float(value)
            elif value_type == 'i':
                return int(value)
            elif value_type == 'n':
                return None
        elif value_dimension == 'l':
            return [ParameterDict._decode(value_type + 's' + x)
                    for x in value.split('0newelement0')]
        else:
            raise ValueError('Unknown {} {}'.format(type(string), string))

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.iteritems():
            self.__setitem__(k, v)
        dict.__init__(self, *args)

    def __setitem__(self, name, value):
        dict.__setitem__(self, name, self._encode(value))

    def __getitem__(self, name):
        return self._decode(dict.__getitem__(self, name))

    def __contains__(self, item):
        return dict.__contains__(self, self._encode(item))

    def __iter__(self):
        return iter((k, self._decode(v)) for (k, v) in self.items())

    def iteritems(self):
        return self.__iter__()

    def get(self, name):
        return self._decode(dict.get(self, name))

    def pop(self, key):
        return self._decode(dict.pop(self, key))

    def popitem(self):
        key, value = dict.popitem(self)
        return (key, self._decode(value))

    def iter_encoded_items(self):
        return dict.iteritems(self)

    def get_encoded_value(self, name):
        return dict.__getitem__(self, name)

    def values(self):
        return [self[k] for k in dict.keys(self)]

    def update(self, *args, **kwargs):
        for d in list(args) + [kwargs]:
            if isinstance(d, ParameterDict):
                dict.update(self, d)
            else:
                for k, v in d.iteritems():
                    self[k] = v
