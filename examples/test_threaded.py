# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import socket
import sys
import threading

try:
    from queue import *
except ImportError:
    from Queue import *

try:
    import SocketServer as socketserver
except ImportError:
    import socketserver

import time

from socketpool.pool import ConnectionPool
from socketpool.conn import TcpConnector

PY3 = sys.version_info[0] == 3

if sys.version_info[0] == 3:
    def s2b(s):
        return s.encode('latin1')
else:
    def s2b(s):
        return s

class EchoHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            self.request.send(data)
            print("echoed %r" % data)

class EchoServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = EchoServer((HOST, PORT), EchoHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever,
            kwargs={"poll_interval":0.5})
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    options = {'host': ip, 'port': port}
    pool = ConnectionPool(factory=TcpConnector, options=options)
    q = Queue()

    def runpool():
        while True:
            try:
                data = q.get(False)
            except Empty:
                break
            try:
                with pool.connection() as conn:
                    print("conn: pool size: %s" % pool.size())
                    sent = conn.send(data)
                    echo = conn.recv(1024)
                    print("got %s" % data)
                    assert data == echo
            finally:
                q.task_done()


    for i in range(20):
        q.put(s2b("Hello World %s" % i), False)

    for i in range(4):
        th = threading.Thread(target=runpool)
        th.daemnon = True
        th.start()

    q.join()

    print ("final pool size: %s" % pool.size())

    pool.release_all()
    server.shutdown()
