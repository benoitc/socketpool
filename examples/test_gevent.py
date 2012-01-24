# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import gevent
from gevent.server import StreamServer

from socketpool.pool import ConnectionPool
from socketpool.conn import TcpConnector

# this handler will be run for each incoming connection in a dedicated greenlet
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
    pool = ConnectionPool(factory=TcpConnector, backend="gevent")
    server = StreamServer(('localhost', 6000), echo)
    gevent.spawn(server.serve_forever)


    def runpool(data):
        print 'ok'
        with pool.connection(**options) as conn:
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
