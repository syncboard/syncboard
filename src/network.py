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

from select import select
from socket import socket, AF_INET, SOCK_STREAM, timeout, error, gethostbyname
from threading import Thread, Lock
import random
import time

TIMEOUT = 0.05
RECV_SIZE = 4096

DEFAULT_PORT = 24749

class Network:
    """Manages all of the network activity for Syncboard.

    Usage:
    n = Network()
    n.start()  # allows network activity to begin

    n.set_clipboard(clipboard_data)

    clipboard_data = n.get_clipboard()

    n.connect(remote_address)

    n.stop()  # cleans up network connections

    Implementation:

    Two background threads -- one to accept new connections, and one to wait to
    receive data.
    """

    def __init__(self, port = DEFAULT_PORT,
                 con_callback = None, dis_callback = None):
        """Initialize the network object, arranging for it to listen on the
        given port.

        In order for network activity to actually start, the start() method must
        be called.

        The connect and disconnect callbacks will be called whenever a peer
        closes the connection. The argument will be the remote address, in
        canonical form. These callbacks may occur in any thread.

        """
        # UID used mostly for conflict resolution
        self.uid = random.randint(0, 0xFFFFFFFF)

        self.port = port

        self._connections = set()
        self._comm_thread = Thread(target=self._comm_loop)
        # if the main thread shuts down, don't wait for the comm thread
        self._comm_thread.daemon = True

        self._server_thread = Thread(target=self._accept_loop)
        self._server_thread.daemon = True

        self.running = False

        self._clipboard = ''

        self.on_connect_callback = con_callback
        self.on_disconnect_callback = dis_callback

    def start(self):
        self.running = True
        self._comm_thread.start()
        self._server_thread.start()

    def set_clipboard(self, data):
        """Threadsafe -- can be called from any thread"""
        # no locking required since this is an atomic operation. We will need
        # locking once we use the sequence number for messages, though.
        self._clipboard = data
        m = Message(self._clipboard)
        for c in self._connections:
            c.send(m)

    def get_clipboard(self):
        """Threadsafe -- can be called from any thread"""
        # no locking required since this is an atomic operation
        return self._clipboard

    def get_clipboard_data_type(self):
        import info
        return info.TXT

    def connect(self, address, port = DEFAULT_PORT):
        # TODO sync clipboard data when connection is established
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((address, port))
        self._setup_connection(s)

    # TODO fix race condition introduced by disconnect
    def disconnect(self, address, port = DEFAULT_PORT):
        """Disconnect from the given peer.

        Disconnect from the given peer, if we are currently connected.
        Otherwise, do nothing.

        Return True if a disconnection took place, False otherwise.

        """

        # get canonical name
        host = gethostbyname(address)
        conn = None
        for c in self._connections:
            if c.get_peer_name() == (host, port):
                conn = c
                break
        if conn:
            self._tear_down_connection(conn)
            return True
        else:
            return False

    def stop(self):
        self.running = False

        # wait for the threads to cleanly exit
        self._server_thread.join()
        self._comm_thread.join()

    def _process_message(self, message):
        """Called when we receive a message over the wire"""
        self._clipboard = message.get_payload()

    def _comm_loop(self):
        while self.running:
            # wait until a socket is ready to read
            if self._connections:
                readlist, _, _ = select(self._connections, [], [], TIMEOUT)
                if readlist:
                    conn = readlist[0]

                    if conn.receive():
                        self._process_message(conn.get_next_message())
                    else:
                        if self.on_disconnect_callback:
                            self.on_disconnect_callback(conn.get_peer_name()[0])
                        self._tear_down_connection(conn)
            else:
                time.sleep(TIMEOUT)

        while self._connections:
            # kinda gross, but we can't iterate over the elements since we
            # remove them in this loop, and we can't pop since we remove them in
            # the tear down method
            conn = iter(self._connections).next()
            self._tear_down_connection(conn)

    def _accept_loop(self):
        server_socket = socket(AF_INET, SOCK_STREAM)

        # bind to all network interfaces
        server_socket.bind(('', self.port))
        # allow the OS to enqueue 5 waiting connections
        server_socket.listen(5)
        # timeout so we can check if we should shut down
        server_socket.settimeout(TIMEOUT)

        while self.running:
            try:
                client_socket, address = server_socket.accept()
                if self.on_connect_callback:
                    self.on_connect_callback(address[0])
            except timeout:
                pass
            else:
                self._setup_connection(client_socket)
        server_socket.close()

    def _setup_connection(self, conn):
        self._connections.add(Connection(conn))

    def _tear_down_connection(self, conn):
        conn.close()
        self._connections.remove(conn)

# TODO add locking if receives and get_next_messages are done in multiple
# threads
class Connection:
    """Manages a socket and other data specific to a connection.

    Holds any data received that does not yet form a complete message.

    """

    def __init__(self, sock):
        self._socket = sock
        # use nonblocking i/o
        self._socket.setblocking(0)
        self._raw_data = ''

    def get_peer_name(self):
        return self._socket.getpeername()

    def receive(self):
        """Perform a nonblocking receive on the underlying socket.

        Return True if data was received, False otherwise. A False return code
        generally means the connection has been severed.

        The received data is available through #get_next_message, if a complete
        message has been received.

        """
        try:
            new_data = self._socket.recv(RECV_SIZE)
        except error as e:
            return False

        self._raw_data += new_data
        return len(new_data) > 0

    def get_next_message(self):
        """Return the next available message, if there is one, or None, if none
        is available"""
        message, self._raw_data = Message.parse_message(self._raw_data)
        return message

    def fileno(self):
        return self._socket.fileno()

    def send(self, message):
        self._socket.sendall(message.raw())

    def close(self):
        self._socket.close()

# TODO fill out the rest of the implementation of this class -- implement the
# more complicated protocol, and then modify the Network class accordingly
class Message:
    """A record type representing a message to be passed over the wire"""

    @staticmethod
    def parse_message(raw_message):
        """Return a Message object representing the data contained in the
        argument, plus any left data left over at the end.

        Return (None, raw_message) if the argument does not represent a valid Message
        """
        m = Message()
        m.set_payload(raw_message)
        return (m, '')

    def __init__(self, payload=''):
        self._payload = payload

    def raw(self):
        """Return a representation of this Message suitable for sending over the
        wire"""
        return self._payload

    def set_payload(self, payload):
        self._payload = payload

    def get_payload(self):
        return self._payload

    def set_uid(self, uid):
        self._uid

    def get_uid(self):
        return self._uid

    def set_sequence_number(self, n):
        self._seq = n;

    def get_sequence_number(self):
        return self._seq

    def __str__(self):
        return self._payload
