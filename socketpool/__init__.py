import gevent
from .pool import ConnectionPool
from .connectors import SocketConnector



if __name__ == '__main__':
    import time

    options = {'host': 'localhost', 'port': 3306}
    pool = ConnectionPool(factory=SocketConnector, options=options)

    def runpool(data):
        print 'ok'
        with pool.connection() as conn:
            print 'sending'
            sent = conn.send(data)
            print 'send %d bytes' % sent
            print conn.recv(1024)

    start = time.time()
    for _ in xrange(4):
        gevent.spawn(runpool, 'blablabl')

    gevent.run()
    delay = time.time() - start
