# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import unittest

from socketpool import ConnectionPool, Connector
from socketpool.pool import MaxTriesError

class MessyConnector(Connector):

    def __init__(self, **options):
        pass

    def is_connected(self):
        return False

    def invalidate(self):
        pass


class PoolTestCase(unittest.TestCase):

    def test_size_on_isconnected_failure(self):
        pool = ConnectionPool(MessyConnector)
        self.assert_(pool.size == 0)
        self.assertRaises(MaxTriesError, pool.get)
