# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import gevent
from gevent import select
from gevent import socket
from gevent import queue

from socketpool.pool import ConnectionPool

try:
    from gevent import lock
except ImportError:
    #gevent < 1.0b2
    from gevent import coros as lock


sleep = gevent.sleep
Semaphore = lock.BoundedSemaphore
Socket = socket.socket
Select = select.select

class PriorityQueue(queue.PriorityQueue):

    def __next__(self):
        try:
            result = self.get(block=False)
        except queue.Empty:
            raise StopIteration
        return result
    next = __next__

class ConnectionReaper(gevent.Greenlet):

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
