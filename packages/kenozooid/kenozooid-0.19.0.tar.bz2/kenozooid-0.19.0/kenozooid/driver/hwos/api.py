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
Implementation of Kenozooid driver API for hwOS family dive computers.
"""

import asyncio
import btzen
import logging

import kenozooid.component as kc
from kenozooid.driver import DeviceDriver, DataParser, DeviceError
from . import parser
from .raw import read_data

logger = logging.getLogger(__name__)

MODELS = sorted(set(parser.MODEL.values()))

@kc.inject(DeviceDriver, id='hwos', name='hwOS Driver', models=MODELS)
class HWOSDriver:
    """
    Driver for hwOS family OSTC dive computers.
    """
    def __init__(self, port):
        self._device = btzen.Serial(port)

    async def connect(self):
        await self._device.connect()

    async def start(self):
        await self._device.write(b'\xbb')
        value = await self._device.read(2)
        assert value == b'\xbb\x4d'

    async def read_data(self, cmd, n, params=None):
        """
        Read data from hwOS OSTC dive computer.

        A command parameters can be set. Parameters are sent before data is
        read.

        The implementation allows to follow hwOS OSTC dive computer
        protocol stricly. For example for `0x66` command

        - get echo byte first
        - then send the dive number

        If above protocol is not followed, then transfer will occasionally
        hang.
        """
        assert len(cmd) == 1

        dev = self._device

        # write command and read echo
        await dev.write(cmd)
        value = await dev.read(1)
        assert value == cmd

        if params:
            await dev.write(params)

        # read: echo and 0x4d marker
        data = await dev.read(n + 1)
        assert data[-1:] == b'\x4d'
        return data[:-1]

    async def close(self):
        await self._device.write(b'\xff')
        self._device.close()

    @staticmethod
    def scan(port=None):
        """
        Look for hwOS based dive computer connected via Bluetooth.

        NOTE: Just connects to a dive computer using given MAC address.

        :param port: Bluetooth MAC address of a dive computer.
        """
        drv = HWOSDriver(port)
        logger.debug('connected hwos based ostc {}'.format(port))
        yield drv

@kc.inject(DataParser, id='hwos', data=('gas',))
class HWOSDataParser(object):
    """
    Dive data parser for hwOS dive computer.

    The data format is

    - version and identity, command 0x69, 64 bytes
    - hardware and features, command 0x60, 5 bytes
    - dive headers, comman 0x61, 65536 bytes
    - dive profiles, command 0x66, variable size depends on dive headers
    """
    def dump(self):
        """
        Download hwOS based dive computer raw data.
        """
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(read_data(self.driver))
        return data

    def version(self, data):
        data = parser.raw_data(data)
        model, major, minor = parser.model_version(data)
        return '{} {}.{:02}'.format(model, major, minor)

    def dives(self, data):
        """
        Convert dive data into UDDF format.
        """
        return parser.parse_dives(data)

# vim: sw=4:et:ai
