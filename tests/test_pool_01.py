# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.

import time

import pytest

from socketpool import ConnectionPool, Connector
from socketpool.pool import MaxTriesError

class MessyConnector(Connector):

    def __init__(self, **options):
        pass

    def is_connected(self):
        return False

    def invalidate(self):
        pass

class Test_Pool(object):
    def test_size_on_isconnected_failure(self):
        pool = ConnectionPool(MessyConnector)
        assert pool.size == 0
        pytest.raises(MaxTriesError, pool.get)

    def test_stop_reaper_thread(self):
        """Verify that calling stop_reaper will terminate the reaper thread.
        """
        pool = ConnectionPool(MessyConnector, backend='thread')
        assert pool._reaper.running
        pool.stop_reaper()

        for i in xrange(1000):
            if not pool._reaper.running:
                return
            time.sleep(0.01)

        assert False, 'Reaper thread not terminated in time.'

    def test_del(self):
        """Verify that garbage collection of the pool will release the reaper
        thread.
        """
        pool = ConnectionPool(MessyConnector, backend='thread')
        reaper = pool._reaper

        assert reaper.running

        # Remove reference.
        pool = None

        for i in xrange(1000):
            if not reaper.running:
                return
            time.sleep(0.01)

        assert False, 'Reaper thread not terminated in time.'
