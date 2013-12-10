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

from select import select
from socket import socket, AF_INET, SOCK_STREAM, timeout, error
from threading import Thread, Lock

TIMEOUT = 0.2
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

    def __init__(self, port = DEFAULT_PORT):
        self.port = port

        self._connections = set()
        self._comm_thread = Thread(target=self._comm_loop)
        # if the main thread shuts down, don't wait for the comm thread
        self._comm_thread.daemon = True

        self._server_thread = Thread(target=self._accept_loop)
        self._server_thread.daemon = True

        self.running = False

    def start(self):
        self.running = True
        self._comm_thread.start()
        self._server_thread.start()

    def set_clipboard(self, data):
        for c in self._connections:
            c.send(data)

    def connect(self, address, port = DEFAULT_PORT):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((address, port))
        self._setup_connection(s)

    def stop(self):
        self.running = False

        # wait for the threads to cleanly exit
        self._server_thread.join()
        self._comm_thread.join()

    def _comm_loop(self):
        while self.running:
            # wait until a socket is ready to read
            readlist, _, _ = select(self._connections, [], [], TIMEOUT)
            if readlist:
                conn = readlist[0]

                if not conn.receive():
                    self._tear_down_connection(conn)
                    continue
                print 'received data: ' + conn.get_next_message()

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
    """Manages a socket and other data specific to a connection"""

    def __init__(self, sock):
        self._socket = sock
        # use nonblocking i/o
        self._socket.setblocking(0)
        self._raw_data = ''

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
        data = self._raw_data
        self._raw_data = ''
        return data

    def fileno(self):
        return self._socket.fileno()

    def send(self, message):
        self._socket.sendall(message)

    def close(self):
        self._socket.close()
