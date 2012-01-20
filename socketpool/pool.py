# -*- coding: utf-8 -
#
# This file is part of socketpool released under the MIT license.
# See the NOTICE for more information.

import sys
import contextlib
try:
    from Queue import Empty, PriorityQueue
except ImportError: # py3
    from queue import Empty, PriorityQueue

import time

class MaxTriesError(Exception):
    pass


class IPriorityQueue(PriorityQueue):

    def __iter__(self):
        return self

    def next(self):
        try:
            result = self.get()
        except Empty:
            raise StopIteration
        return result


class ConnectionPool(object):
    QUEUE_CLASS = IPriorityQueue
    SLEEP = time.sleep

    def __init__(self, factory,
                 retry_max=3, retry_delay=.1,
                 timeout=-1, max_lifetime=600.,
                 max_size=10, options=None):
        self.max_size = max_size
        self.pool = self.QUEUE_CLASS()
        self.size = 0
        self.factory = factory
        self.retry_max = retry_max
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.max_lifetime = max_lifetime
        if options is None:
            self.options = {}
        else:
            self.options = options

    def too_old(self, conn):
        return time.time() - conn.get_lifetime() > self.max_lifetime

    def release_connection(self, conn):
        connected = conn.is_connected()
        if connected and not self.too_old(conn):
            self.pool.put((conn.get_lifetime(), conn))
        else:
            conn.invalidate()

    def get(self, **options):
        pool = self.pool

        # first let's try to find a matching one
        found = None
        if self.size >= self.max_size or pool.qsize():
            for priority, candidate in pool:
                if self.too_old(candidate):
                    # let's drop it
                    continue

                matches = candidate.matches(**options)
                if not matches:
                    # let's put it back
                    pool.put((priority, candidate))
                else:
                    found = candidate
                    break

        # we got one.. we use it
        if found is not None:
            print "reuse"
            return found

        print "new"

        # we build a new one and send it back
        tries = 0
        last_error = None

        while tries < self.retry_max:
            self.size += 1
            try:
                new_item = self.factory(**options)
            except Exception, e:
                self.size -= 1
                last_error = e
            else:
                # we should be connected now
                if new_item.is_connected():
                    return new_item

            tries += 1
            self.SLEEP(self.retry_delay)

        if last_error is None:
            raise MaxTriesError()
        else:
            raise last_error


    @contextlib.contextmanager
    def connection(self, **options):
        options.update(self.options)
        conn = self.get(**options)
        try:
            yield conn
            # what to do in case of success
        except Exception, e:
            conn.handle_exception(e)
        finally:
            self.release_connection(conn)

