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
Raw data reader for hwOS OSTC dive computer.
"""

from .parser import COMMANDS, dive_headers_data, dive_profile_size, to_int

import logging

logger = logging.getLogger(__name__)

async def read_data(drv):
    """
    Fetch raw data from hwOS based dive computer.

    :param drv: hwOS dive computer driver.

    .. seealso:: `HWOSDataParser.dump`
    """
    await drv.connect()
    try:
        await drv.start()
        data = [await drv.read_data(b, n) for b, n in COMMANDS]
        assert len(data) == 3

        headers = data[2]
        assert len(headers) == 65536, [len(v) for v in data]

        profiles = await dive_profiles(drv, headers)
        data.extend(profiles)

        return b''.join(data)
    finally:
        await drv.close()

async def dive_profiles(drv, headers):
    """
    Read raw data of all dive profiles.

    :param drv: hwOS OSTC dive computer driver.
    :param headers: Dive headers raw data.
    """
    headers = dive_headers_data(headers)
    sizes = (dive_profile_size(v) for v in headers)
    return [await dive_profile(drv, k, n) for k, n in enumerate(sizes)]

async def dive_profile(drv, k, n):
    """
    Read dive profile raw data of a single dive.

    :param drv: hwOS OSTC dive computer driver.
    :param k: Dive number.
    :param n: Size of dive profile data to be read.
    """
    # dive profile data includes header data, so add 256
    size = n + 256 - 3
    dive_no = bytes([k])
    data = await drv.read_data(b'\x66', size, params=dive_no)

    head = data[:256]
    profile = data[256:]

    assert head[:2] == b'\xfa\xfa', head[:2]
    assert head[-2:] == b'\xfb\xfb', head[-2:]
    assert n == to_int(profile[:3])
    assert profile[-2:] == b'\xfd\xfd', profile[-2:]

    return profile

# vim: sw=4:et:ai
