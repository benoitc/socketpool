
from socketpool import Connector, ConnectionPool
from socketpool.pool import MaxTriesError
import pytest

class MessyConnector(Connector):
    def __init__(self, **options):
        pass

    def is_connected(self):
        return False

    def invalidate(self):
        pass

def test_size_on_isconnected_failure():
    pool = ConnectionPool(MessyConnector)
    assert pool.size == 0
    pytest.raises(MaxTriesError, pool.get)
    assert pool.size == 0
