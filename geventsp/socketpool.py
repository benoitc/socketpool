from geventsp.pool import Connector
from gevent import socket
import socket
import time


class SocketConnector(Connector):

    def __init__(self, host, port):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((host, port))
        self.host = host
        self.port = port
        self._connected = True
        self._life = time.time()

    def matches(self, **match_options):
        target_host = match_options.get('host')
        target_port = match_options.get('port')
        return target_host == self.host and target_port == self.port

    def is_connected(self):
        return self._connected

    def handle_exception(self, exception):
        print 'got an exception'
        print str(exception)

    def is_old(self, max_lifetime):
        return time.time() - self._life > max_lifetime

    def invalidate(self):
        self._s.close()
        self._connected = False
        self._life = -1

    def send(self, data):
        return self._s.send(data)

    def recv(self, size=1024):
        return self._s.recv(size)
