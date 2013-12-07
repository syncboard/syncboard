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

MAX_ALIAS_LENGTH = 15
MAX_ADDRESS_LENGTH = 15

class ConnectionManager:
    def __init__(self):
        self.connections = []

    def get_connection(self, address):
        for con in self.connections:
            if con.address == address:
                return con
        return None

    def new_connection(self, alias, address):
        self.connections.append(Connection(alias, address, Connection.PENDING))

    def del_connection(self, address):
        c = self.get_connection(address)
        if c:
            self.connections.remove(c)

class Connection:
    NOT_CONNECTED, CONNECTED, PENDING, REQUEST = range(4)
    def __init__(self, alias, address, status):
        self.alias = alias
        self.address = address
        self.status = status

    def __str__(self):
        return "%s (%s) Status: %s" %(self.address, self.alias, self.status)
