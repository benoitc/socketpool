# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import contextlib
import sys
import time

from socketpool.util import load_backend

class MaxTriesError(Exception):
    pass


class ConnectionPool(object):

    def __init__(self, factory,
                 retry_max=3, retry_delay=.1,
                 timeout=-1, max_lifetime=600.,
                 max_size=10, options=None,
                 reap_connections=True,
                 backend="thread"):

        self.backend_mod = load_backend(backend)

        self.max_size = max_size
        self.pool = self.backend_mod.PriorityQueue()
        self.size = 0
        self.factory = factory
        self.retry_max = retry_max
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.max_lifetime = max_lifetime
        if options is None:
            self.options = {"backend_mod": self.backend_mod}
        else:
            self.options = options
            self.options["backend_mod"] = self.backend_mod

        self._reaper = None
        if reap_connections:
            self.start_reaper()

    def too_old(self, conn):
        return time.time() - conn.get_lifetime() > self.max_lifetime

    def murder_connections(self):
        pool = self.pool
        if pool.qsize():
            for priority, candidate in pool:
                if not self.too_old(candidate):
                    pool.put((priority, candidate))

    def start_reaper(self):
        self._reaper = self.backend_mod.ConnectionReaper(self,
                delay=self.max_lifetime)
        self._reaper.ensure_started()


    def release_connection(self, conn):
        if self._reaper is not None:
            self._reaper.ensure_started()

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
            return found


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
            self.backend_mod.sleep(self.retry_delay)

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

