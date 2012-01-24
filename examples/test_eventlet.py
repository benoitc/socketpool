# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import eventlet

from socketpool.pool import ConnectionPool
from socketpool.conn import TcpConnector


# this handler will be run for each incoming connection in a dedicated greenlet

class EchoServer(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.spool = eventlet.GreenPool()
        self.running = False
        self.server = None

    def start(self):
        eventlet.spawn(self.run)

    def run(self):
        self.server = eventlet.listen((self.host, self.port))
        self.running = True
        while self.running:
            try:
                sock, address = self.server.accept()
                print "accepted", address
                self.spool.spawn_n(self.handle, sock, address)
            except (SystemExit, KeyboardInterrupt):
                break


    def handle(self, sock, address):
        print ('New connection from %s:%s' % address)

        while True:
            data = sock.recv(1024)
            if not data:
                break
            sock.send(data)
            print ("echoed %r" % data)


    def stop(self):
        self.running = False


if __name__ == '__main__':
    import time

    options = {'host': 'localhost', 'port': 6000}
    pool = ConnectionPool(factory=TcpConnector, options=options,
            backend="eventlet")
    server = EchoServer('localhost', 6000)
    server.start()

    epool = eventlet.GreenPool()
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
    _ = [epool.spawn(runpool, "blahblah") for _ in xrange(20)]

    epool.waitall()
    server.stop()
    delay = time.time() - start
