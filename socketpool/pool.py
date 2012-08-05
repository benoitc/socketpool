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

class MaxConnectionsError(Exception):
    pass

class ConnectionPool(object):
    """Pool of connections

    This is the main object to maintain connection. Connections are
    created using the factory instance passed as an option.

    Options:
    --------

    :attr factory: Instance of socketpool.Connector. See
        socketpool.conn.TcpConnector for an example
    :attr retry_max: int, default 3. Numbr of times to retry a
        connection before raising the MaxTriesError exception.
    :attr max_lifetime: int, default 600. time in ms we keep a
        connection in the pool
    :attr max_size: int, default 10. Maximum number of connections we
        keep in the pool.
    :attr options: Options to pass to the factory
    :attr reap_connection: boolean, default is true. If true a process
        will be launched in background to kill idle connections.
    :attr backend: string, default is thread. The socket pool can use
        different backend to handle process and connections. For now
        the backends "thread", "gevent" and "eventlet" are supported. But
        you can add your own backend if you want. For an example of backend,
        look at the module socketpool.gevent_backend.
    """

    def __init__(self, factory,
                 retry_max=3, retry_delay=.1,
                 timeout=-1, max_lifetime=600.,
                 max_size=10, options=None,
                 reap_connections=True, backend="thread"):

        self.backend_mod = load_backend(backend)
        self.backend = backend
        self.max_size = max_size
        self.pool = getattr(self.backend_mod, 'PriorityQueue')()
        self._free_conns = 0
        self.factory = factory
        self.retry_max = retry_max
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.max_lifetime = max_lifetime
        if options is None:
            self.options = {"backend_mod": self.backend_mod,
                            "pool": self}
        else:
            self.options = options
            self.options["backend_mod"] = self.backend_mod
            self.options["pool"] = self

        # bounded semaphore to make self._alive 'safe'
        self._sem = self.backend_mod.Semaphore(1)

        self._reaper = None
        if reap_connections:
            self.start_reaper()

    def too_old(self, conn):
        return time.time() - conn.get_lifetime() > self.max_lifetime

    def murder_connections(self):
        current_pool_size = self.pool.qsize()
        if current_pool_size > 0:
            for priority, candidate in self.pool:
                current_pool_size -= 1
                if not self.too_old(candidate):
                    self.pool.put((priority, candidate))
                else:
                    self._reap_connection(candidate)
                if current_pool_size <= 0:
                    break

    def start_reaper(self):
        self._reaper = self.backend_mod.ConnectionReaper(self,
                delay=self.max_lifetime)
        self._reaper.ensure_started()

    def _reap_connection(self, conn):
        if conn.is_connected():
            conn.invalidate()

    def size(self):
        return self.pool.qsize()

    def release_all(self):
        if self.pool.qsize():
            for priority, conn in self.pool:
                self._reap_connection(conn)

    def release_connection(self, conn):
        if self._reaper is not None:
            self._reaper.ensure_started()

        with self._sem:
            if self.pool.qsize() < self.max_size:
                connected = conn.is_connected()
                if connected and not self.too_old(conn):
                    self.pool.put((conn.get_lifetime(), conn))
                else:
                    self._reap_connection(conn)
            else:
                self._reap_connection(conn)

    def get(self, **options):
        options.update(self.options)

        found = None
        i = self.pool.qsize()
        tries = 0
        last_error = None

        unmatched = []

        while tries < self.retry_max:
            # first let's try to find a matching one from pool

            if self.pool.qsize():
                for priority, candidate in self.pool:
                    i -= 1
                    if self.too_old(candidate):
                        # let's drop it
                        self._reap_connection(candidate)
                        continue

                    matches = candidate.matches(**options)
                    if not matches:
                        # let's put it back
                        unmatched.append((priority, candidate))
                    else:
                        if candidate.is_connected():
                            found = candidate
                            break
                        else:
                            # conn is dead for some reason.
                            # reap it.
                            self._reap_connection(candidate)

                    if i <= 0:
                        break

            if unmatched:
                for candidate in unmatched:
                    self.pool.put(candidate)

            # we got one.. we use it
            if found is not None:
                return found

            try:
                new_item = self.factory(**options)
            except Exception as e:
                last_error = e
            else:
                # we should be connected now
                if new_item.is_connected():
                    with self._sem:
                        return new_item

            tries += 1
            self.backend_mod.sleep(self.retry_delay)

        if last_error is None:
            raise MaxTriesError()
        else:
            raise last_error

    @contextlib.contextmanager
    def connection(self, **options):
        conn = self.get(**options)
        try:
            yield conn
            # what to do in case of success
        except Exception as e:
            conn.handle_exception(e)
        finally:
            self.release_connection(conn)

