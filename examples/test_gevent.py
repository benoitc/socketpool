import gevent
from gevent.server import StreamServer

from socketpool.gpool import GConnectionPool, GSocketConnector


# this handler will be run for each incoming connection in a dedicated greenlet
def echo(sock, address):
    print ('New connection from %s:%s' % address)

    data = sock.recv(1024)

    sock.send(data)
    print ("echoed %r" % data)



if __name__ == '__main__':
    import time

    options = {'host': 'localhost', 'port': 6000}
    pool = GConnectionPool(factory=GSocketConnector, options=options)
    server = StreamServer(('localhost', 6000), echo)
    gevent.spawn(server.start)


    def runpool(data):
        print 'ok'
        with pool.connection() as conn:
            print 'sending'
            sent = conn.send(data)
            print 'send %d bytes' % sent
            data = conn.recv(1024)
            print "got %s" % data
            assert data == "blahblah"

    start = time.time()
    jobs = [gevent.spawn(runpool, "blahblah") for _ in xrange(4)]

    gevent.joinall(jobs)
    delay = time.time() - start
