# -*- coding: utf-8 -
#
# This file is part of socketpool released under the MIT license.
# See the NOTICE for more information.

import gevent
from gevent import socket
from gevent.queue import PriorityQueue


from .pool import ConnectionPool
from .conn import SocketConnector

class GConnectionPool(ConnectionPool):
    QUEUE_CLASS = PriorityQueue
    SLEEP = gevent.sleep


class GSocketConnector(SocketConnector):
    SOCKET_CLASS = socket.socket
