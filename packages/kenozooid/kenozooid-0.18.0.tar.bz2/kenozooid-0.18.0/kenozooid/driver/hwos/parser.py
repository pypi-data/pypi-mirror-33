#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2018 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Data parser for hwOS family OSTC dive computers driver.
"""

import enum
import logging
import operator
import struct
from datetime import datetime
from functools import partial
from itertools import takewhile
from collections import namedtuple
from cytoolz import itertoolz as itz
from cytoolz.functoolz import identity

import kenozooid.data as kd
import kenozooid.units as ku
from kenozooid.util import cumsum

logger = logging.getLogger(__name__)

COMMANDS = (
    (b'\x69', 64),     # version identity
    (b'\x60', 5),      # hardware + features
    (b'\x61', 65536),  # dive headers
)

# page 9 of hwOS interface documentation
MODEL = {
    0x0a: 'OSTC 3',
    0x1a: 'OSTC 3+',
    0x05: 'OSTC cR',
    0x07: 'OSTC cR',
    0x12: 'OSTC Sport',
    0x11: 'OSTC 2',
    0x13: 'OSTC 2',
    0x1b: 'OSTC 2',
    # 0x13: 'OSTC 3+',
    # 0x13: 'OSTC Sport',
}

# note: gauge -> opencircuit
DIVE_MODES = 'opencircuit', 'closedcircuit', 'opencircuit', 'apnoe'

# the minimal size of a dive profile sample
#
# - two bytes for depth
# - profile flag byte
MIN_SAMPLE_SIZE = 3

RawData = namedtuple('Data', ['version', 'features', 'headers', 'profiles'])
RawData.__doc__ = """
Raw data fetched from a hwOS family OSTC dive computer.
"""

Header = namedtuple(
    'Header',
    [
        'size', 'datetime', 'depth', 'duration', 'temp', 'gas_list',
        'avg_depth', 'mode'
    ],
)

ProfileHeader = namedtuple('ProfileHeader', ['size', 'rate', 'divs'])
Divisor = namedtuple('Divisor', ['type', 'size', 'divisor'])
Events = namedtuple('Events', ['alarm', 'events'])
EventData = namedtuple(
    'EventData',
    ['manual_gas', 'gas', 'setpoint', 'bailout']
)

to_int = partial(int.from_bytes, byteorder='little', signed=False)
to_timestamp = lambda v: datetime(v[0] + 2000, *v[1:])
to_depth = lambda v: v * 9.80665 / 1000
to_duration = lambda v: to_int(v[:2]) * 60 + int(v[2])
to_temp = lambda v: v / 10
to_gas = lambda v: kd.gas(int(v[0]), int(v[1])) if v else None
to_gas_list = lambda data: [
    kd.gas(o2, he, depth) for o2, he, depth, _ in itz.partition(4, data)
]

class EventFlags(enum.IntFlag):
    """
    Event flags.

    Event flags do not contain alarm information.

    As described at page 6 of hwOS interface documentation.
    """
    MANUAL_GAS = 1
    GAS = 2
    SET_POINT = 4
    # 8: always unset, skipping bit indicating next event byte
    BAILOUT = 16

def raw_data(data):
    cmd_len = [n for _, n in COMMANDS]
    items = partition(data, *cumsum(cmd_len, 0))
    result = RawData(*items)
    assert all(len(item) == n for n, item in zip(cmd_len, result))
    return result

def parse_dives(data):
    data = raw_data(data.data)
    headers = dive_headers_data(data.headers)
    headers = [parse_header(v) for v in headers]

    # note: hwos header size stated in header raw data includes 3 more
    # bytes, why?
    idx = cumsum((h.size - 3 for h in headers), 0)
    profiles = partition(data.profiles, *idx)
    yield from (create_dive(h, p) for h, p in zip(headers, profiles))

def parse_profile(header, data):
    """
    Parse dive profile raw data.

    :param header: Dive header.
    :param data: Dive profile raw data.
    """
    assert data[-2:] == b'\xfd\xfd', data[-2:]

    p_header = parse_profile_header(data)
    assert p_header.size == header.size

    start = len(p_header.divs) * 3 + 5
    profile = data[start:-2]

    idx = dive_profile_sample_idx(profile)
    samples = partition(profile, *idx)
    samples = enumerate(samples, 1)
    samples = (create_sample(header, p_header, k, s) for k, s in samples)
    # omit shallow/surface part
    samples = takewhile(lambda s: s.time <= header.duration, samples)

    assert header.gas_list
    first_gas = itz.first(m for m in header.gas_list if m.depth == 0)
    assert first_gas is not None

    yield kd.Sample(depth=0, time=0, gas=first_gas)
    yield from samples
    yield kd.Sample(depth=0, time=header.duration + p_header.rate)

def parse_events(data):
    """
    Parse event data from event bytes of dive profile sample raw data.

    :param data: Dive profile sample raw data.
    """
    items = takewhile(lambda v: v & 0x80, data[2:])
    k = itz.count(items)

    event_bytes_start = 3 + k
    items = data[3:event_bytes_start]
    value = to_int(v & ~0x80 for v in items)

    alarm = value & 0x07
    events = EventFlags(value >> 4)

    event_data = parse_event_data(events, data[event_bytes_start:])
    return Events(alarm, event_data)

def parse_event_data(events, data):
    """
    Parse event data from a raw data of a sample of a dive profile.

    :param events: Event flags.
    :param data: Raw data of a sample of a dive profile.
    """
    sizes = 2, 1, 1, 2
    items = zip(EventFlags, sizes)
    # keep event byte size if flag is set, zero it if not, so non-existing
    # event byte results in empty string
    items = (bool(events & f) * s for f, s in items)
    idx = cumsum(items, 0)

    manual_gas, gas, setpoint, bailout, *_ = partition(data, *idx)
    manual_gas = to_gas(manual_gas)
    gas = to_int(gas) if gas else None
    setpoint = to_int(setpoint) / 100 if setpoint else None
    bailout = to_gas(bailout)
    return EventData(manual_gas, gas, setpoint, bailout)

def model_version(data):
    """
    Get model and version information about a hwOS family OSTC dive
    computer.

    :param data: Raw data fetched from a hwOS family OSTC dive computer.

    .. seealso:: `RawData`
    """
    major, minor = data.version[2:4]
    dsc = data.features[1]
    model = MODEL.get(dsc, 'OSTC hwOS')
    logger.debug('descriptor 0x{:x} -> model {}'.format(dsc, model))
    return model, major, minor

def parse_header(data):
    """
    Parse dive header data read from hwOS OSTC dive computer.
    """
    parsers = (
        identity,  # start marker
        to_int, to_timestamp, to_depth, to_duration, to_temp,
        to_gas_list,
        # average depth, dive mode
        to_depth, identity,
        identity  # end marker
    )
    # 5s - datetime, 20s - gas list, B - dive mode
    fmt = '<H 7x 3s 5s H 3s h 4x 20s 25x H 7x B 171x H'
    fields = header_fields(parsers, fmt, data)
    return Header._make(fields)

def parse_profile_header(data):
    """
    Parse dive profile header (aka small header).

    :param data: Dive profile data.
    """
    size, rate, no_div = struct.unpack('3sBB', data[:5])
    size = to_int(size)

    divs = data[5:5 + 3 * no_div]
    assert len(divs) == 3 * no_div
    divs = struct.unpack('BBB' * no_div, divs)
    divs = itz.partition(3, divs)
    divs = tuple(Divisor._make(v) for v in divs)

    return ProfileHeader(size, rate, divs)

def dive_profile_size(data):
    """
    Extract dive profile size from dive header raw data.
    """
    parsers = (identity, to_int, identity)
    fmt = '<H7x3s242xH'
    data = header_fields(parsers, fmt, data)
    return data[0]

def dive_headers_data(headers):
    """
    Divide all dive header raw data into collection of raw data for each
    header.

    :param headers: Raw header data fetched from hwOS OSTC dive computer.
    """
    assert len(headers) == 65536

    items = itz.partition(256, headers)
    # convert back to bytes, see
    #
    # - https://github.com/pytoolz/cytoolz/issues/102
    # - https://github.com/pytoolz/toolz/issues/377
    #
    # also filter unused headers via `logbook-profile version` header field
    yield from (bytes(v) for v in items if v[8] != 0xff)

def header_fields(parsers, fmt, data):
    """
    Extract dive header fields data from dive header raw data.

    :param parsers: Parser for each field, including start and end markers.
    :param fmt: Struct format to extract the fields.
    :param data: Dive header raw data.
    """
    assert struct.calcsize(fmt) == 256, struct.calcsize(fmt)

    items = struct.unpack(fmt, data)
    items = zip(parsers, items)
    start, *fields, end = (p(v) for p, v in items)
    assert start == 0xfafa and end == 0xfbfb, '0x{:x} 0x{:x}'.format(start, end)

    return fields

def dive_profile_sample_idx(data):
    """
    Determine index of each dive profile sample using the profile raw data.

    :param data: Dive profile raw data.
    """
    # there is no more than `n_samples` dive profile samples
    n_samples = len(data) // MIN_SAMPLE_SIZE

    f = partial(dive_profile_next_sample, data)
    idx = itz.accumulate(f, range(n_samples))
    idx = takewhile(lambda i: i < len(data), idx)
    return idx

def dive_profile_next_sample(data, idx, sample_no):
    """
    Calculate index of next dive profile sample.

    The calculation is performed using dive profile raw data and index of
    current dive profile sample. The `idx + 2` points to profile flag byte,
    which is used to determine total length of current sample.

    :param data: Dive profile raw data.
    :param idx: Index of current dive profile sample.
    :param sample_no: Sample number (unused).
    """
    return idx + (data[idx + 2] & 0x7f) + MIN_SAMPLE_SIZE

def partition(data, *idx):
    """
    Partition the data using indexes.

    Each index is start of each item.

    :param data: Data to partition.
    :param idx: Indexes used to partition the data.
    """
    item_range = idx + (None,)
    item_range = zip(item_range[:-1], item_range[1:])
    yield from (data[j:k] for j, k in item_range)

def create_dive(header, data):
    """
    Create Kenozooid dive record.

    :param header: Dive header of a dive stored in hwOS OSTC dive computer.
    :param data: Dive profile raw data.
    """
    return kd.Dive(
        datetime=header.datetime,
        depth=header.depth,
        duration=header.duration,
        temp=ku.C2K(header.temp),
        avg_depth=header.avg_depth,
        mode=DIVE_MODES[header.mode],
        profile=list(parse_profile(header, data)),
    )

def create_sample(header, profile_header, sample_no, data):
    """
    Create Kenozooid dive profile sample record.

    :param header: Dive header.
    :param profile_header: Dive profile header.
    :param sample_no: Dive profile sample number.
    :param data: Dive profile sample data.
    """
    depth = to_depth(to_int(data[:2]))
    time = sample_no * profile_header.rate

    events = parse_events(data)
    assert events.events.gas is None or events.events.gas > 0
    gas = header.gas_list[events.events.gas - 1] if events.events.gas else None
    manual_gas = events.events.manual_gas if events.events.manual_gas else None

    if __debug__ and gas:
        logger.debug('Dive {}, gas number: {}, gas: {}'.format(
            header.datetime, events.events.gas, gas
        ))

    alarm = ('deco',) if events.alarm == 2 else None
    return kd.Sample(
        depth=depth,
        time=time,
        gas=gas,
        alarm=alarm,
    )

# vim: sw=4:et:ai
