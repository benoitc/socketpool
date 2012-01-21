# -*- coding: utf-8 -
#
# This file is part of socketpool released under the MIT license.
# See the NOTICE for more information.

import gevent
from gevent import socket
from gevent.queue import PriorityQueue


from socketpool.pool import ConnectionPool
from socketpool.conn import SocketConnector

class GeventConnectionReaper(gevent.Greenlet):

    running = False

    def __init__(self, pool, delay=150):
        self.pool = pool
        self.delay = delay
        gevent.Greenlet.__init__(self)

    def _run(self):
        self.running = True
        while True:
            gevent.sleep(self.delay)
            self.pool.murder_connections()

    def ensure_started(self):
        if not self.running or self.ready():
            self.start()

class GConnectionPool(ConnectionPool):
    QUEUE_CLASS = PriorityQueue
    SLEEP = gevent.sleep
    REAPER_CLASS = GeventConnectionReaper

class GSocketConnector(SocketConnector):
    SOCKET_CLASS = socket.socket
