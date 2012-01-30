# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import eventlet
from eventlet import sleep
from eventlet.green.select import select as Select
from eventlet.green.socket import socket as Socket
from eventlet.queue import PriorityQueue, Empty as QueueEmpty


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
