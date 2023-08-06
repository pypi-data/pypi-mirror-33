#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2018
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

import sys
import unittest

import crc32c
crc32 = crc32c.crc32

if sys.version_info[0] == 2:
    def as_individual_bytes(x):
        return x
else:
    def as_individual_bytes(x):
        for b in x:
            yield bytes([b])

class TestCrc32c(unittest.TestCase):

    check = 0xe3069283

    def test_all(self):
        self.assertEqual(self.check, crc32(b'123456789'))

    def test_piece_by_piece(self):
        c = crc32(b'1')
        for x in as_individual_bytes(b'23456789'):
            c = crc32(x, c)
        self.assertEqual(self.check, c)