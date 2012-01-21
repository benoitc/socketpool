# -*- coding: utf-8 -
#
# This file is part of socketpool released under the MIT license.
# See the NOTICE for more information.


import eventlet
from eventlet.green import socket
from eventlet.queue import PriorityQueue


from socketpool.pool import ConnectionPool
from socketpool.conn import SocketConnector

class EventletConnectionReaper(object):

    running = False

    def __init__(self, pool, delay=150):
        self.pool = pool
        self.delay = delay

    def start(self):
        self.running = True
        g = eventlet.spawn(self._exec)
        g.link(self._exit)

    def _exit(self, g):
        try:
            g.wait()
        except:
            pass
        self.running = False

    def _exec(self):
        while True:
            eventlet.sleep(self.delay)
            self.pool.murder_connections()

    def ensure_started(self):
        if not self.running:
            self.start()

class EConnectionPool(ConnectionPool):
    QUEUE_CLASS = PriorityQueue
    SLEEP = eventlet.sleep
    REAPER_CLASS = EventletConnectionReaper

class ESocketConnector(SocketConnector):
    SOCKET_CLASS = socket.socket
