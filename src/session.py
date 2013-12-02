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

"""
    Session is the class that manages all the non UI work. Any UI implementation
    would create and interact with an instance of a Session to provide actual
    functionality.
"""

from connections import ConnectionManager, Connection

class Session:
    def __init__(self):
        # TODO: consider saving and loading the connections list to a file
        #       to preserve the list between sessions
        self.con_mgr = ConnectionManager()

    def connections(self):
        return self.con_mgr.connections

    def get_connection(self, address):
        return self.con_mgr.get_connection(address)

    def new_connection(self, alias, address):
        self.con_mgr.new_connection(alias, address)

    def accept_connection(self, address):
        conn = self.get_connection(address)
        if conn:
            print "Connection from %s accepted" % address
            conn.status = Connection.CONNECTED
        else:
            print "Error: no connection from %s exists"

    def del_connection(self, address):
        self.con_mgr.del_connection(address)

