import pytest
from socketpool.pool import ConnectionPool
from socketpool.conn import TcpConnector

def make_and_check_backend(expected_name, **kw):
    pool = ConnectionPool(TcpConnector, **kw)
    assert pool.backend == expected_name
    return pool


def test_default_backend():
    make_and_check_backend('thread')


def test_thread_backend():
    make_and_check_backend('thread', backend='thread')


def test_gevent_backend():
    pytest.importorskip('gevent')
    make_and_check_backend('gevent', backend='gevent')


def test_eventlet_backend():
    pytest.importorskip('eventlet')
    make_and_check_backend('eventlet', backend='eventlet')


def test_thread_backend_as_module():
    from socketpool import backend_thread
    make_and_check_backend('socketpool.backend_thread', backend=backend_thread)
