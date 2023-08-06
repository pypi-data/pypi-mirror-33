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
Unit tests for parser of driver for hwOS family of OSTC dive computers.
"""

from cytoolz.functoolz import identity
from datetime import datetime

import kenozooid.data as kd
from kenozooid.driver.hwos import parser

import pytest

DEFAULT_GAS_LIST = [(kd.gas(21, 0), parser.GAS_TYPE_FIRST)]

def test_model_version():
    """
    Test getting model and version.
    """
    data = parser.RawData(b'\x00\x01\x0a\x23', b'\x00\x1b', b'', b'')
    model, major, minor = parser.model_version(data)
    assert 'OSTC 2' == model
    assert 10 == major
    assert 35 == minor

def test_dive_profile_size():
    """
    Test extracting dive profile size data from raw header data.
    """
    data = b'\xfa\xfa' + 7 * b'\x00' \
        + b'\x23\x01\x00' \
        + 242 * b'\x00' + b'\xfb\xfb'
    assert len(data) == 256  # pre-condition

    size = parser.dive_profile_size(data)
    assert 0x123 == size

def test_dive_headers_data():
    """
    Test getting a collection of raw header data from all header raw data.
    """
    create = lambda v: b'\x00' * 8 + v + 247 * b'\x00'
    data = [create(b'\x23') for i in range(4)]
    data.extend(create(b'\xff') for i in range(256 - 8))
    data.extend(create(b'\x23') for i in range(4))
    data = b''.join(data)

    headers = parser.dive_headers_data(data)
    headers = list(headers)
    assert len(headers) == 8

def test_header_fields():
    """
    Test extracting header fields data from dive header raw data.
    """
    data = b'\xfa\xfa' + b'\x01\x02\x03' + 249 * b'\x00' + b'\xfb\xfb'
    assert len(data) == 256  # pre-condition

    fmt = '<H2sB249xH'
    parsers = identity, parser.to_int, identity, identity
    data = parser.header_fields(parsers, fmt, data)
    assert len(data) == 2
    assert 0x0201 == data[0]
    assert 0x03 == data[1]

def test_partition():
    """
    Test partitioning data using indexes.
    """
    data = list(range(10))
    v1, v2, v3, v4 = parser.partition(data, 0, 3, 7, 8)

    assert [0, 1, 2] == v1
    assert [3, 4, 5, 6] == v2
    assert [7] == v3
    assert [8, 9] == v4

def test_partition_empty():
    """
    Test partitioning data using indexes with empty data.
    """
    data = list(range(10))
    v1, v2, v3, v4, v5 = parser.partition(data, 0, 3, 3, 7, 8)

    assert [0, 1, 2] == v1
    assert [] == v2
    assert [3, 4, 5, 6] == v3
    assert [7] == v4
    assert [8, 9] == v5

def test_dive_profile_sample_idx():
    """
    Test calculation of indexes of dive profile samples.
    """
    data = [
        3, 2, 4, 11, 11, 11, 11,  # 4 bytes more
        3, 2, 0,                  # min sample size
        3, 2, 2, 33, 33,          # 2 bytes more
        3, 2, 0,
    ]
    idx = parser.dive_profile_sample_idx(data)
    assert [0, 7, 10, 15] == list(idx)

def test_dive_profile_next_sample():
    """
    Test calculationn of index of next dive profile sample.
    """
    data = [3, 2, 4, 0, 0, 0, 0, 3, 2, 0]
    r = parser.dive_profile_next_sample(data, 0, 0)
    assert 7 == r

def test_create_dive():
    """
    Test creating Kenozooid dive record for hwOS dive computer dive.
    """
    header = parser.Header(
        size=0,
        datetime=datetime(2017, 1, 1),
        depth=33,
        duration=1000,
        temp=298.15,
        gas_list=DEFAULT_GAS_LIST,
        avg_depth=20,
        mode=0,
    )
    # 0 size, 16s sampling rate, 0 divisors
    dive = parser.create_dive(header, b'\x00\x00\x00\x10\x00\xfd\xfd')

    assert datetime(2017, 1, 1) == dive.datetime
    assert 33 == dive.depth
    assert 1000 == dive.duration
    assert 298.15 == pytest.approx(dive.temp)
    assert 20 == dive.avg_depth
    assert 'opencircuit' == dive.mode

def test_create_sample():
    """
    Test creating Kenozooid dive profile sample record for hwOS dive
    computer dive.
    """
    header = parser.Header(
        size=0,
        datetime=datetime(2017, 1, 1),
        depth=33,
        duration=1000,
        temp=25,
        gas_list=DEFAULT_GAS_LIST,
        avg_depth=20,
        mode=0,
    )

    p_header = parser.ProfileHeader(0, 10, [])
    data = b'\x64\x00\x82\x02'

    # set temp to 285K and deco info to 12m for 3min
    ext_parser = lambda v: (285, (12, 3)) +  (None,) * 5

    sample = parser.create_sample(header, p_header, ext_parser, 3, data)
    assert 0.980665 == sample.depth
    assert 30 == sample.time
    assert ('deco',) == sample.alarm
    assert 285 == sample.temp
    assert 12 == sample.deco_depth
    assert 3 == sample.deco_time

def test_parse_empty_dive_profile():
    """
    Test parsing empty dive profile.
    """
    header = parser.Header(
        size=0,
        datetime=datetime(2017, 1, 1),
        depth=33,
        duration=1000,
        temp=25,
        gas_list=DEFAULT_GAS_LIST,
        avg_depth=20,
        mode=0,
    )
    data = b'\x00\x00\x00\x10\x00\xfd\xfd'
    samples = parser.parse_profile(header, data)

    s1, s2 = samples
    assert 0 == s1.depth
    assert 0 == s1.time

    assert 0 == s1.depth
    assert 1016 == s2.time  # header.duration + rate

def test_parse_events():
    """
    Test parsing events.
    """
    result = parser.parse_events(b'\x00\x00\x00\x10\x11')
    assert 0 == result.alarm
    assert (None,) * 4 == result.events

    result = parser.parse_events(b'\x00\x00\x80\x01\x10\x11')
    assert 0x01 == result.alarm
    assert (None,) * 4 == result.events

    result = parser.parse_events(b'\x00\x00\x80\x81\x02\x10\x11')
    assert 0x01 == result.alarm
    assert (None,) * 4 == result.events

    result = parser.parse_events(b'\x00\x00\x80\x84\x82\03\x10\x11')
    assert 0x04 == result.alarm
    assert (None,) * 4 == result.events

def test_parse_event_data():
    """
    Test parsing of event data.
    """
    result = parser.parse_event_data(0b10111, b'\x0a\x32\x01\x6e\x15\x00')
    assert 10 == result.manual_gas.o2
    assert 50 == result.manual_gas.he
    assert 1 == result.gas
    assert 1.1 == result.setpoint
    assert 21 == result.bailout.o2
    assert 0 == result.bailout.he

    result = parser.parse_event_data(0b00110, b'\x02\x6e')
    assert 2 == result.gas
    assert 1.1 == result.setpoint

    result = parser.parse_event_data(0b10100, b'\x6e\x15\x00')
    assert 1.1 == result.setpoint
    assert 21 == result.bailout.o2
    assert 0 == result.bailout.he

# vim: sw=4:et:ai
