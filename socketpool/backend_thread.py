# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import select
import socket
import threading
import time
import weakref

try:
    import Queue as queue
except ImportError: # py3
    import queue

Select = select.select
Socket = socket.socket
sleep = time.sleep
Semaphore = threading.BoundedSemaphore


class PriorityQueue(queue.PriorityQueue):

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.get(block=False)
        except queue.Empty:
            raise StopIteration
        return result
    next = __next__

class ConnectionReaper(threading.Thread):
    """ connection reaper thread. Open a thread that will murder iddle
    connections after a delay """

    running = False
    forceStop = False

    def __init__(self, pool, delay=600):
        self.pool = weakref.ref(pool)
        self.delay = delay
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        self.running = True
        while True:
            time.sleep(self.delay)
            pool = self.pool()
            if pool is not None:
                pool.murder_connections()

            if self.forceStop:
                self.running = False
                break

    def ensure_started(self):
        if not self.running and not self.is_alive():
            self.start()
