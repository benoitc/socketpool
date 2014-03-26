from socketpool.pool import ConnectionPool
from socketpool.conn import TcpConnector

def pytest_generate_tests(metafunc):
    if 'backend' in metafunc.fixturenames:
        metafunc.parametrize('backend', ['thread', 'gevent', 'eventlet'])

class Test_Backend(object):
    def make_and_check_backend(self, expected_name, **kw):
        pool = ConnectionPool(TcpConnector, **kw)
        assert pool.backend == expected_name
        return pool

    def test_default_backend(self):
        self.make_and_check_backend('thread')

    def test_backend(self, backend):
        self.make_and_check_backend(backend, backend=backend)

    def test_thread_backend_as_module(self):
        from socketpool import backend_thread
        self.make_and_check_backend('socketpool.backend_thread',
                                    backend=backend_thread)
