socketpool
----------

Socketpool - a simple Python socket pool.

Socket pool is a simple socket pool that sumport multiple factory and
backend. It can easily be used by gevent, eventlet or any other library.

Usage
-----

socketpool offers 3 main classes, a `ConnectionPool` class abble to
accept a factory and a backend, `Connector` and interface class
inherited by all connector and a default TCP connector `TcpConnector` .


Example of a simple echo client using Gevent
--------------------------------------------

::

    import gevent
    from gevent.server import StreamServer

    from socketpool import ConnectionPool, TcpConnector

    # this handler will be run for each incoming connection
    # in a dedicated greenlet
    def echo(sock, address):
        print ('New connection from %s:%s' % address)

        while True:
            data = sock.recv(1024)
            if not data:
                break
            sock.send(data)
            print ("echoed %r" % data)



    if __name__ == '__main__':
        import time

        options = {'host': 'localhost', 'port': 6000}
        pool = ConnectionPool(factory=TcpConnector, options=options,
                backend="gevent")
        server = StreamServer(('localhost', 6000), echo)
        gevent.spawn(server.serve_forever)


        def runpool(data):
            print 'ok'
            with pool.connection() as conn:
                print 'sending'
                sent = conn.send(data)
                print 'send %d bytes' % sent
                echo_data = conn.recv(1024)
                print "got %s" % data
                assert data == echo_data

        start = time.time()
        jobs = [gevent.spawn(runpool, "blahblah") for _ in xrange(20)]

        gevent.joinall(jobs)
        delay = time.time() - start


Example of a connector
----------------------

::

    class TcpConnector(Connector):

        def __init__(self, host, port, backend_mod):
            self._s = backend_mod.Socket(socket.AF_INET, socket.SOCK_STREAM)
            self._s.connect((host, port))
            self.host = host
            self.port = port
            self._connected = True
            self._life = time.time()

        def matches(self, **match_options):
            target_host = match_options.get('host')
            target_port = match_options.get('port')
            return target_host == self.host and target_port == self.port

        def is_connected(self):
            return self._connected

        def handle_exception(self, exception):
            print 'got an exception'
            print str(exception)

        def get_lifetime(self):
            return self._life

        def invalidate(self):
            self._s.close()
            self._connected = False
            self._life = -1

        def send(self, data):
            return self._s.send(data)

        def recv(self, size=1024):
            return self._s.recv(size)


Authors
-------

- Benoît Chesneau (benoitc) <benoitc@e-engura.org>
- Tarek Ziade (tarek) <tarek@ziade.org>

License
-------

socketpool is available in the public domain (see UNLICENSE). socketpool
is also optionally available under the MIT License (see LICENSE), meant
especially for jurisdictions that do not recognize public domain works.
