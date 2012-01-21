# -*- coding: utf-8 -
#
# This file is part of socketpool released under the MIT license.
# See the NOTICE for more information.


import eventlet
from eventlet.green import socket
from gevent.queue import PriorityQueue


from socketpool.pool import ConnectionPool
from socketpool.conn import SocketConnector

class GConnectionPool(ConnectionPool):
    QUEUE_CLASS = PriorityQueue
    SLEEP = eventlet.sleep


class GSocketConnector(SocketConnector):
    SOCKET_CLASS = socket.socket
