import logging
import time
from threading import Lock
from typing import Optional, Any, Dict, Union
from queue import Queue

import rethinkdb as R
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.3.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['PoolException', 'ConnectionPool']

_log = logging.getLogger(__name__)
RethinkDBConnection = Any  # pylint: disable=invalid-name
RETRY_ATTEMPTS = 20


class PoolException(Exception):
    pass


class ConnectionWrapper(object):
    def __init__(
            self, pool: 'ConnectionPool',
            conn: Optional[RethinkDBConnection] = None, **kwargs) -> None:
        self._pool = pool
        if conn is None:
            self._conn = R.connect(**kwargs)
        else:
            self._conn = conn
        self.connected_at = time.time()

    @property
    def connection(self) -> RethinkDBConnection:
        return self._conn

    @property
    def expire(self) -> bool:
        if not self._pool.connection_ttl:
            return False
        now = time.time()
        return (now - self.connected_at) > self._pool.connection_ttl  # type: ignore


class ConnectionContextManager:

    __slots__ = ('pool', 'timeout', 'looped_mode', 'conn')

    def __init__(
            self, pool: 'ConnectionPool',
            timeout: Optional[int] = None, looped_mode: bool = False) -> None:
        self.pool = pool
        self.timeout = timeout
        self.looped_mode = looped_mode
        self.conn: Optional[RethinkDBConnection] = None

    def __enter__(self):
        self.conn = self.pool.acquire(self.timeout)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if self.looped_mode:
                self.pool.release_to_looped(self.conn)
            else:
                self.pool.release(self.conn)


class ConnectionPool(object):
    """A rethinkDB connection pool
    >>> pool = ConnectionPool()
    >>> with pool.acquire() as conn:
            conn.do_something()
    """

    __slots__ = (
        'pool_size', 'connection_ttl', '_current_acquired',
        'connection_kwargs', '_pool', '_looped_pool', '_pool_lock'
    )

    def __init__(
            self, rethinkdb_connection_kwargs: Dict[str, Union[str, int]],
            pool_size: int = 10, connection_ttl: int = 3600) -> None:
        self.pool_size = pool_size
        self.connection_ttl = connection_ttl
        self.connection_kwargs = rethinkdb_connection_kwargs

        self._pool: Queue = Queue()
        self._looped_pool: Queue = Queue()
        self._pool_lock = Lock()
        self._current_acquired = 0

    def init_pool(self) -> None:
        self._pool_lock.acquire()
        for _ in range(0, self.pool_size):
            self._pool.put(self.new_conn())
        self._pool_lock.release()

    def new_conn(self) -> ConnectionWrapper:
        """
        Create a new ConnectionWrapper instance
        """
        _log.debug("Opening new connection to rethinkdb with args=%s", self.connection_kwargs)
        return ConnectionWrapper(self, **self.connection_kwargs)

    @retry(wait=wait_exponential(multiplier=0.3, max=10), retry=retry_if_exception_type(PoolException), stop=stop_after_attempt(RETRY_ATTEMPTS))
    def acquire(self, timeout: Optional[int] = None) -> RethinkDBConnection:
        """Acquire a connection
        :param timeout: If provided, seconds to wait for a connection before raising
            Queue.Empty. If not provided, blocks indefinitely.
        :returns: Returns a RethinkDB connection
        :raises Empty: No resources are available before timeout.
        """
        if self._current_acquired == self.pool_size:
            raise PoolException("Connection pool is full, please, increase pool size")
        self._pool_lock.acquire()
        _log.debug(
            'Try to acquire, still acquired %d, pool size %d',
            self._current_acquired, self.pool_size
        )
        if timeout is None:
            conn_wrapper = self._pool.get_nowait()
        else:
            conn_wrapper = self._pool.get(True, timeout)
        if conn_wrapper.expire:
            _log.debug('Recreate connection due to ttl expire')
            conn_wrapper.connection.close()
            conn_wrapper = self.new_conn()
        self._current_acquired += 1
        self._pool_lock.release()
        return conn_wrapper.connection

    def release(self, conn: RethinkDBConnection) -> None:
        """Release a previously acquired connection.
        The connection is put back into the pool."""
        self._pool_lock.acquire()
        self._pool.put(ConnectionWrapper(self, conn))
        self._current_acquired -= 1
        self._pool_lock.release()

    def release_to_looped(self, conn: RethinkDBConnection) -> None:
        self._pool_lock.acquire()
        self._looped_pool.put(ConnectionWrapper(self, conn))
        self._current_acquired -= 1
        self._pool_lock.release()

    def empty(self) -> bool:
        """Check pool emptyness
        """
        return self._pool.empty()

    def release_pool(self) -> None:
        """Release pool and all its connection"""
        if self._current_acquired > 0:
            raise PoolException("Can't release pool: %d connection(s) still acquired" % self._current_acquired)
        for target_pool in (self._pool, self._looped_pool):
            while not target_pool.empty():
                conn = self.acquire()
                conn.close()

    def connect(self, timeout: Optional[int] = None, looped_mode: bool = False) -> ConnectionContextManager:
        '''Acquire a new connection with `with` statement and auto release the connection after
            go out the with block

        :param timeout: @see #aquire
        :returns: Returns a RethinkDB connection
        :raises Empty: No resources are available before timeout.
        '''
        return ConnectionContextManager(self, timeout, looped_mode)
