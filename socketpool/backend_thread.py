# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import socket
import threading
import time

try:
    import Queue as queue
except ImportError: # py3
    import queue

Socket = socket.socket
sleep = time.sleep

class PriorityQueue(queue.PriorityQueue):

    def __iter__(self):
        return self

    def next(self):
        try:
            result = self.get(block=False)
        except queue.Empty:
            raise StopIteration
        return result

class ConnectionReaper(threading.Thread):
    """ connection reaper thread. Open a thread that will murder iddle
    connections after a delay """

    running = False

    def __init__(self, pool, delay=600):
        self.pool = pool
        self.delay = delay
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        self.running = True
        while True:
            time.sleep(self.delay)
            self.pool.murder_connections()

    def ensure_started(self):
        if not self.running and not self.isAlive():
            self.start()


