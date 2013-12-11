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

"""
    Session is the class that manages all the non UI work. Any UI implementation
    would create and interact with an instance of a Session to provide actual
    functionality.
"""

from connections import ConnectionManager, Connection
from network import Network

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

        # TODO add command line switch to change port, which would be passed in
        # here
        self._network = Network(con_callback=self._new_connection_request,
                                dis_callback=self._disconnect_request)
        self._network.start()

    def _new_connection_request(self, address):
        conn = self._con_mgr.get_connection(address)
        if conn:
            #conn.status = Connection.REQUEST
            conn.status = Connection.CONNECTED
        else:
            #self._con_mgr.new_connection("", address, Connection.REQUEST)
            self._con_mgr.new_connection("", address, Connection.CONNECTED)

    def _disconnect_request(self, address):
        conn = self._con_mgr.get_connection(address)
        if conn:
            conn.status = Connection.NOT_CONNECTED

    def get_clipboard_data(self):
        self._clipboard_data = self._network.get_clipboard()
        return self._clipboard_data

    def get_clipboard_data_type(self):
        self._data_type = self._network.get_clipboard_data_type()
        return self._data_type

    def get_clipboard_data_owner(self):
        return self._data_owner

    def set_clipboard_data(self, data, data_type):
        """
            This is called (by the gui) when the user pastes to the app.
        """
        self._clipboard_data = data
        self._network.set_clipboard(self._clipboard_data)
        self._data_type = data_type
        self._data_owner = None

    def connections(self):
        """
            Returns a list of all the connections
        """
        return self._con_mgr.connections

    def get_connection(self, address):
        """
            Returns the Connection object that has the given address
        """
        return self._con_mgr.get_connection(address)

    def new_connection(self, alias, address):
        """
            Creates a new Connection to the given address and if there is
            a Syncboard app running at that address then that user will
            see a new connection appear (with the address on this end) with
            status REQUEST.

            After this has executed:
            New Connection on both ends.
            Connection on this end status: PENDING
            Conneciton on other end status: REQUEST
        """
        self._network.connect(address)
        self._con_mgr.new_connection(alias, address)

    def accept_connection(self, address):
        """
            Called when the user accepts the request from the Connection with
            the given address. Meaning, there was a Connection with status
            REQUEST and user accepted it.

            Before this is called:
            Connection on this end status: REQUEST
            Conneciton on other end status: PENDING

            After this has executed:
            Connection on this end status: CONNECTED
            Conneciton on other end status: CONNECTED
        """
        conn = self.get_connection(address)
        if conn:
            print "Connection from %s accepted" % address
            conn.status = Connection.CONNECTED
        else:
            print "Error: no connection from %s exists" % address

    def request_connection(self, address):
        """
            This is like new_connection except in this case the Connection
            with the given address already existed and had status NOT_CONNECTED.

            Before this is called:
            Connection on this end status: NOT_CONNECTED
            Conneciton on other end status: NOT_CONNECTED

            After this has executed:
            Connection on this end status: PENDING
            Conneciton on other end status: REQUEST
        """
        self._network.connect(address)
        conn = self.get_connection(address)
        if conn:
            print "Request to connect to %s sent" % address
            #conn.status = Connection.PENDING
            conn.status = Connection.CONNECTED
        else:
            print "Error: no connection to %s exists" % address

    def disconnect(self, address):
        """
            This is called when the user has an open connection to the given
            address and wants to close the connection.

            Before this is called:
            Connection on this end status: CONNECTED
            Conneciton on other end status: CONNECTED

            After this has executed:
            Connection on this end status: NOT_CONNECTED
            Conneciton on other end status: NOT_CONNECTED
        """
        self._network.disconnect(address)
        conn = self.get_connection(address)
        if conn:
            print "Disconnected from %s" % address
            conn.status = Connection.NOT_CONNECTED
        else:
            print "Error: no connection to %s exists" % address    

    def cancel_request(self, address):
        """
            This is called when the user has requested a connection to the given
            address and the request is still pending but the user wants to
            cancel the request.

            Before this is called:
            Connection on this end status: PENDING
            Conneciton on other end status: REQUEST

            After this has executed:
            Connection on this end status: NOT_CONNECTED
            Conneciton on other end status: NOT_CONNECTED
        """
        conn = self.get_connection(address)
        if conn:
            print "Request to %s canceled" % address
            conn.status = Connection.NOT_CONNECTED
        else:
            print "Error: no connection to %s exists" % address

    def del_connection(self, address):
        """
            Removes the Connection with the given address from the list of
            connections.
        """
        conn = self.get_connection(address)
        if conn:
            if conn.status == Connection.CONNECTED:
                self.disconnect(address)
            self._con_mgr.del_connection(address)
        else:
            print "Error: no connection to %s exists" % address

    def update_alias(self, address, new_alias):
        """
            Changes the alias of the Connection with the given address to be
            new_alias.
        """
        conn = self.get_connection(address)
        if conn:
            print "Updated alias of %s to %s" % (address, new_alias)
            conn.alias = new_alias
        else:
            print "Error: no connection to %s exists" % address
