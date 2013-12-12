"""
    Cross-platform clipboard syncing tool
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

WAIT_TIME = 0.1

class TestSimple(unittest.TestCase):
    def setUp(self):
        self.port1 = random.randint(20000, 30000)
        self.port2 = random.randint(20000, 30000)
        self.n1 = Network(self.port1)
        self.n2 = Network(self.port2)
        self.n1.start()
        self.n2.start()

        # give everything time to get going
        time.sleep(WAIT_TIME)

        # establish connection
        self.n2.connect('localhost', self.port1)
        time.sleep(WAIT_TIME)

    # test simple clipboard syncing
    def test_simple(self):
        m1 = 'test 1'
        self.n2.set_clipboard(m1)
        time.sleep(WAIT_TIME)

        self.assertEqual(self.n1.get_clipboard(), m1)

        m2 = 'test 2'
        self.n1.set_clipboard(m2)
        time.sleep(WAIT_TIME)

        self.assertEqual(self.n2.get_clipboard(), m2)

    def test_disconnect_from_client(self):
        self.n2.set_clipboard('test')
        time.sleep(WAIT_TIME)
        self.assertEqual(self.n1.get_clipboard(), 'test')

        self.n2.disconnect('localhost')
        time.sleep(WAIT_TIME)

        m = "test %d" % random.randint(0, 1000)
        self.n2.set_clipboard(m)
        time.sleep(WAIT_TIME)

        self.assertNotEqual(self.n1.get_clipboard(), m)

    def test_disconnect_from_server(self):
        self.n2.set_clipboard('test')
        time.sleep(WAIT_TIME)
        self.assertEqual(self.n1.get_clipboard(), 'test')

        self.n1.disconnect('localhost')
        time.sleep(WAIT_TIME)

        m = "test %d" % random.randint(0, 1000)
        self.n2.set_clipboard(m)
        time.sleep(WAIT_TIME)

        self.assertNotEqual(self.n1.get_clipboard(), m)

    def test_reconnect(self):
        self.n2.disconnect('localhost')
        time.sleep(WAIT_TIME)
        self.n1.connect('localhost', self.port2)
        time.sleep(WAIT_TIME)

        self.n1.set_clipboard('asdf 5')
        time.sleep(WAIT_TIME)
        self.assertEqual(self.n2.get_clipboard(), 'asdf 5')

    def tearDown(self):
        # give it enough time to execute before tearing down
        time.sleep(WAIT_TIME)
        self.n1.stop()
        self.n2.stop()

class TestConnect(unittest.TestCase):
    def test_connect(self):
        port1 = random.randint(20000, 30000)
        port2 = random.randint(20000, 30000)
        n1 = Network(port1)
        n2 = Network(port2)
        n1.start()
        n2.start()
        time.sleep(WAIT_TIME)

        m = 'hasdgbaeswbjf'
        n2.set_clipboard(m)
        time.sleep(WAIT_TIME)

        n1.connect('localhost', port2)
        time.sleep(WAIT_TIME)

        self.assertEqual(m, n1.get_clipboard())

        n1.stop()
        n2.stop()
