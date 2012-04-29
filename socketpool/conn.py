# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import select
import socket
import time

class Connector(object):
    def matches(self, **match_options):
        raise NotImplementedError()

    def is_connected(self):
        raise NotImplementedError()

    def handle_exception(self, exception):
        raise NotImplementedError()

    def get_lifetime(self):
        raise NotImplementedError()

    def invalidate(self):
        raise NotImplementedError()


class TcpConnector(Connector):

    def __init__(self, host, port, backend_mod, pool=None):
        self._s = backend_mod.Socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((host, port))
        self.host = host
        self.port = port
        self.backend_mod = backend_mod
        self._connected = True
        self._life = time.time()
        self._pool = pool

    def __del__(self):
        self.release()

    def matches(self, **match_options):
        target_host = match_options.get('host')
        target_port = match_options.get('port')
        return target_host == self.host and target_port == self.port

    def is_connected(self):
        if self._connected:
            try:
                r, _, _ = self.backend_mod.Select([self._s], [], [], 0)
                if not r:
                    return True
            except (ValueError, select.error,):
                return False
        return False

    def handle_exception(self, exception):
        print 'got an exception'
        print str(exception)

    def get_lifetime(self):
        return self._life

    def invalidate(self):
        self._s.close()
        self._connected = False
        self._life = -1

    def release(self):
        if self._pool is not None:
            if self._connected:
                self._pool.release_connection(self)
            else:
                self._pool = None

    def send(self, data):
        return self._s.send(data)

    def recv(self, size=1024):
        return self._s.recv(size)
