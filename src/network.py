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
from Queue import Queue, Empty

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

        self._connection_thread = ConnectionThread(self._process_message, self._run_disconnect_callback)

        self._server_thread = Thread(target=self._accept_loop)
        self._server_thread.daemon = True

        self._running = False

        self._clipboard = ''

        # a queue of connections that need to be made. Contains Connection
        # objects that must be added to the _connections set.
        self._connect_queue = Queue()
        # a queue of (address, port) pairs to be disconnected from
        self._disconnect_queue = Queue()
        # a queue of Message objects to be sent
        self._send_queue = Queue()

        self._on_connect_callback = con_callback
        self._on_disconnect_callback = dis_callback

    def start(self):
        self._running = True
        self._connection_thread.start()
        self._server_thread.start()

    def set_clipboard(self, data):
        """Threadsafe -- can be called from any thread"""
        # no locking required since this is an atomic operation. We will need
        # locking once we use the sequence number for messages, though.
        self._clipboard = data
        m = Message(self._clipboard)
        self._connection_thread.send(m)

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
        self._connection_thread.add_connection(Connection(s))

    def disconnect(self, address, port = None):
        """Disconnect from the given peer.

        Disconnect from the given peer, if we are currently connected.
        Otherwise, do nothing.

        If a port number is given, disconnect from the peer that is connected
        from the given port. Otherwise, disconnect from any peer at the given
        address. Note that if no port is given, behavior is undefined if there
        are connections to multiple peers at the given address.

        """
        self._connection_thread.schedule_disconnect(address, port)

    def stop(self):
        self._running = False

        # wait for the threads to cleanly exit
        self._server_thread.join()
        self._connection_thread.stop()

    def _run_disconnect_callback(self, *args):
        if self._on_disconnect_callback:
          self._on_disconnect_callback(*args)

    def _process_message(self, message):
        """Called when we receive a message over the wire"""
        self._clipboard = message.get_payload()

    def _accept_loop(self):
        server_socket = socket(AF_INET, SOCK_STREAM)

        # bind to all network interfaces
        server_socket.bind(('', self.port))
        # allow the OS to enqueue 5 waiting connections
        server_socket.listen(5)
        # timeout so we can check if we should shut down
        server_socket.settimeout(TIMEOUT)

        while self._running:
            try:
                client_socket, address = server_socket.accept()
                if self._on_connect_callback:
                    self._on_connect_callback(*address)
            except timeout:
                pass
            else:
                self._connection_thread.add_connection(Connection(client_socket))
        server_socket.close()

class ConnectionThread:
    """Manages the connection thread, and accepts messages from any thread on
    its behalf.

    All the publicly accessible methods may be called from any thread.

    There should probably be only one instance of this object.

    """

    def __init__(self, msg_recv_callback, disconnect_callback):
        self._msg_recv_callback = msg_recv_callback
        self._disconnect_callback = disconnect_callback

        self._thread = Thread(target=self._loop)
        self._thread.daemon = True

        # Queue of Message objects
        self._message_queue = Queue()
        # Queue of Connection objects to be added to _connections
        self._connection_queue = Queue()
        # Queue of (address, port) pairs indicating peers to disconnect from
        self._disconnect_queue = Queue()

        self._running = False

        self._connections = set()

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def add_connection(self, connection):
        """Takes a Connection object"""
        self._connection_queue.put(connection)

    def schedule_disconnect(self, address, port):
        self._disconnect_queue.put((address, port))

    def send(self, message):
        """Sends the given message to all peers"""
        self._message_queue.put(message)

    def _loop(self):
        while self._running:
            self._process_sends()
            self._process_receive()
            self._process_new_conns()
            self._process_disconnects()

        while self._connections:
            # kinda gross, but we can't iterate over the elements since we
            # remove them in this loop, and we can't pop since we remove them in
            # the tear down method
            conn = iter(self._connections).next()
            self._tear_down_connection(conn)

    def _process_sends(self):
        try:
            while True:
                # raises Empty when it's empty
                message = self._message_queue.get_nowait()
                for c in self._connections:
                    c.send(message)
        except Empty:
            pass

    def _process_new_conns(self):
        try:
            while True:
                # raises Empty when it's empty
                c = self._connection_queue.get_nowait()
                self._connections.add(c)
        except Empty:
            pass

    def _process_disconnects(self):
        try:
            while True:
                # raises Empty when it's empty
                address, port = self._disconnect_queue.get_nowait()
                # get canonical name
                host = gethostbyname(address)

                conn = None
                for c in self._connections:

                    # only enforce equal ports if a port was given
                    if port is None:
                        condition = c.get_peer_name()[0] == host
                    else:
                        condition = c.get_peer_name(0) == (host, port)

                    if condition:
                        conn = c
                        break
                if conn:
                    self._tear_down_connection(conn)
        except Empty:
            pass

    def _process_receive(self):
        """Helper method for the connection loop.

        Either processes the receipt of data from a single connection, or blocks
        for TIMEOUT
        seconds

        """
        # wait until a socket is ready to read
        if self._connections:
            readlist, _, _ = select(self._connections, [], [], TIMEOUT)
            if readlist:
                conn = readlist[0]

                if conn.receive():
                    self._msg_recv_callback(conn.get_next_message())
                else:
                    if self._disconnect_callback:
                        self._disconnect_callback(conn.get_peer_name()[0])
                    self._tear_down_connection(conn)
        else:
            time.sleep(TIMEOUT)

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
