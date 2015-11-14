# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import socket
import time
import random

from socketpool import util

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


class UnixConnector(Connector):

    def __init__(self, socket_file, backend_mod, pool=None):
        self._s = backend_mod.Socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket_file = socket_file
        self._s.connect(self.socket_file)
        self.backend_mod = backend_mod
        self._connected = True
        self._life = time.time() - random.randint(0, 10)
        self._pool = pool

    def __del__(self):
        self.release()

    def matches(self, **match_options):
        target_sock = match_options.get('socket_file')
        return target_sock == self.socket_file

    def is_connected(self):
        if self._connected:
            return util.is_connected(self._s)
        return False

    def handle_exception(self, exception):
        print('got an exception')
        print(str(exception))

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



class TcpConnector(Connector):

    def __init__(self, host, port, backend_mod, pool=None, mode='r',
                 bufsize=-1):
        self._s = backend_mod.Socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((host, port))
        self._s_file = self._s.makefile(mode, bufsize)
        self.host = host
        self.port = port
        self.backend_mod = backend_mod
        self._connected = True
        # use a 'jiggle' value to make sure there is some
        # randomization to expiry, to avoid many conns expiring very
        # closely together.
        self._life = time.time() - random.randint(0, 10)
        self._pool = pool

    def __del__(self):
        self.release()

    def matches(self, **match_options):
        target_host = match_options.get('host')
        target_port = match_options.get('port')
        return target_host == self.host and target_port == self.port

    def is_connected(self):
        if self._connected:
            return util.is_connected(self._s)
        return False

    def handle_exception(self, exception):
        print('got an exception')
        print(str(exception))

    def get_lifetime(self):
        return self._life

    def invalidate(self):
        self._s.close()
        self._s_file.close()
        self._connected = False
        self._life = -1

    def release(self):
        if self._pool is not None:
            if self._connected:
                self._pool.release_connection(self)
            else:
                self._pool = None

    def read(self, size=-1):
        return self._s_file.read(size)

    def readline(self, size=-1):
        return self._s_file.readline(size)

    def readlines(self, sizehint=0):
        return self._s_file.readlines(sizehint)

    def sendall(self, *args):
        return self._s.sendall(*args)

    def send(self, data):
        return self._s.send(data)

    def recv(self, size=1024):
        return self._s.recv(size)
