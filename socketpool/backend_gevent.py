# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

from socketpool.util import NonbockingPriorityQueueMixin

import gevent
from gevent import sleep
from gevent.select import select as Select
from gevent.socket import socket as Socket
from gevent import queue

class PriorityQueue(NonbockingPriorityQueueMixin, queue.PriorityQueue):
    Empty = queue.Empty

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
