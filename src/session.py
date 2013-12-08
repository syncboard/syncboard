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
        self._con_mgr = ConnectionManager()

        # The data on the common clipboard.
        self._clipboard_data = None
        # Type of data on the clipboard (eg. text, bitmap, etc.)
        # This should be one of the supported types in info.py
        self._data_type = None
        # None will mean that this client is owner, otherwise it should be a
        # Connection object.
        self._data_owner = None

    def get_clipboard_data(self):
        return self._clipboard_data

    def get_clipboard_data_type(self):
        return self._data_type

    def get_clipboard_data_owner(self):
        return self._data_owner

    def set_clipboard_data(self, data, data_type):
        self._clipboard_data = data
        self._data_type = data_type
        self._data_owner = None

    def connections(self):
        return self._con_mgr.connections

    def get_connection(self, address):
        return self._con_mgr.get_connection(address)

    def new_connection(self, alias, address):
        self._con_mgr.new_connection(alias, address)

    def accept_connection(self, address):
        conn = self.get_connection(address)
        if conn:
            print "Connection from %s accepted" % address
            conn.status = Connection.CONNECTED
        else:
            print "Error: no connection from %s exists" % address

    def request_connection(self, address):
        conn = self.get_connection(address)
        if conn:
            print "Request to connect to %s sent" % address
            conn.status = Connection.PENDING
        else:
            print "Error: no connection to %s exists" % address

    def disconnect(self, address):
        conn = self.get_connection(address)
        if conn:
            print "Disconnected from %s" % address
            conn.status = Connection.NOT_CONNECTED
        else:
            print "Error: no connection to %s exists" % address    

    def cancel_request(self, address):
        conn = self.get_connection(address)
        if conn:
            print "Request to %s canceled" % address
            conn.status = Connection.NOT_CONNECTED
        else:
            print "Error: no connection to %s exists" % address

    def del_connection(self, address):
        self._con_mgr.del_connection(address)

