"""
    Cross-platform clipboard sycning tool
    Copyright (C) 2013  Syncboard

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import random
import time
import unittest

from network import Network

WAIT_TIME = 0.5

class TestSimple(unittest.TestCase):
    def setUp(self):
        print 'setup'
        self.port1 = random.randint(20000, 30000)
        self.port2 = random.randint(20000, 30000)
        self.n1 = Network(self.port1)
        self.n2 = Network(self.port2)
        self.n1.start()
        self.n2.start()
        # give everything time to get going
        time.sleep(WAIT_TIME)

    def test_connect(self):
        print 'connecting...'
        self.n2.connect('localhost', self.port1)
        time.sleep(WAIT_TIME)
        print 'sending 1...'
        self.n2.set_clipboard('testing 1')
        print 'sending 2...'
        self.n1.set_clipboard('testing 2')
        # give it enough time to execute before tearing down
        print 'sleeping...'
        time.sleep(WAIT_TIME)
        print 'done sleeping...'

    def tearDown(self):
        self.n1.stop()
        self.n2.stop()
