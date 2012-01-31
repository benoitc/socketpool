# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import eventlet
from eventlet.green import select
from eventlet.green import socket
from eventlet import queue

from socketpool.pool import ConnectionPool

sleep = eventlet.sleep
Socket = socket.socket
Select = select.select

class PriorityQueue(queue.PriorityQueue):

    def __iter__(self):
        return self

    def next(self):
        try:
            result = self.get(block=False)
        except queue.Empty:
            raise StopIteration
        return result

class ConnectionReaper(object):

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
