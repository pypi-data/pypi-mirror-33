"""
This module holds a rough implementation of the C# TCP client.

This class is **not** safe across several tasks since partial reads
may be ``await``'ed before being able to return the exact byte count.

This class is also not concerned about disconnections or retries of
any sort, nor any other kind of errors such as connecting twice.
"""
import threading
import errno
import logging
import socket
from io import BytesIO

CONN_RESET_ERRNOS = {
    errno.EBADF, errno.ENOTSOCK, errno.ENETUNREACH,
    errno.EINVAL, errno.ENOTCONN, errno.EHOSTUNREACH,
    errno.ECONNREFUSED, errno.ECONNRESET, errno.ECONNABORTED,
    errno.ENETDOWN, errno.ENETRESET, errno.ECONNABORTED,
    errno.EHOSTDOWN, errno.EPIPE, errno.ESHUTDOWN
}
# catched: EHOSTUNREACH, ECONNREFUSED, ECONNRESET, ENETUNREACH
# ConnectionError: EPIPE, ESHUTDOWN, ECONNABORTED, ECONNREFUSED, ECONNRESET

try:
    import socks
except ImportError:
    socks = None

__log__ = logging.getLogger(__name__)


class TcpClient:
    """A simple TCP client to ease the work with sockets and proxies."""

    class SocketClosed(ConnectionError):
        pass

    def __init__(self, *, timeout, proxy=None):
        """
        Initializes the TCP client.

        :param proxy: the proxy to be used, if any.
        :param timeout: the timeout for connect, read and write operations.
        """
        self.proxy = proxy
        self._socket = None
        self._closed = threading.Event()
        self._closed.set()

        if isinstance(timeout, (int, float)):
            self.timeout = float(timeout)
        elif hasattr(timeout, 'seconds'):
            self.timeout = float(timeout.seconds)
        else:
            raise TypeError('Invalid timeout type: {}'.format(type(timeout)))

    @staticmethod
    def _create_socket(mode, timeout, proxy):
        if proxy is None:
            s = socket.socket(mode, socket.SOCK_STREAM)
        else:
            import socks
            s = socks.socksocket(mode, socket.SOCK_STREAM)
            if isinstance(proxy, dict):
                s.set_proxy(**proxy)
            else:  # tuple, list, etc.
                s.set_proxy(*proxy)
        s.settimeout(timeout)
        return s

    def connect(self, ip, port):
        """
        Tries connecting to IP:port unless an OSError is raised.

        :param ip: the IP to connect to.
        :param port: the port to connect to.
        """
        if ':' in ip:  # IPv6
            ip = ip.replace('[', '').replace(']', '')
            mode, address = socket.AF_INET6, (ip, port, 0, 0)
        else:
            mode, address = socket.AF_INET, (ip, port)

        try:
            if self._socket is None:
                self._socket = self._create_socket(
                    mode, self.timeout, self.proxy)

            self._socket.connect(address)
            self._closed.clear()
        except OSError as e:
            if e.errno in CONN_RESET_ERRNOS:
                raise ConnectionResetError() from e
            else:
                raise

    @property
    def is_connected(self):
        """Determines whether the client is connected or not."""
        return not self._closed.is_set()

    def close(self):
        """Closes the connection."""
        try:
            if self._socket is not None:
                fd = self._socket.fileno()
                if self.is_connected:
                    self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
        except OSError:
            pass  # Ignore ENOTCONN, EBADF, and any other error when closing
        finally:
            self._socket = None
            self._closed.set()

    def write(self, data):
        """
        Writes (sends) the specified bytes to the connected peer.
        :param data: the data to send.
        """
        if not self.is_connected:
            raise ConnectionResetError('Not connected')

        try:
            self._socket.sendall(data)
        except OSError as e:
            if e.errno in CONN_RESET_ERRNOS:
                raise ConnectionResetError() from e
            else:
                raise

    def read(self, size):
        """
        Reads (receives) a whole block of size bytes from the connected peer.

        :param size: the size of the block to be read.
        :return: the read data with len(data) == size.
        """
        if not self.is_connected:
            raise ConnectionResetError('Not connected')

        with BytesIO() as buffer:
            bytes_left = size
            while bytes_left != 0:
                try:
                    partial = self._socket.recv(bytes_left)
                except socket.timeout:
                    if bytes_left < size:
                        __log__.warning(
                            'Timeout when partial %d/%d had been received',
                            size - bytes_left, size
                        )
                    raise
                except OSError as e:
                    if e.errno in CONN_RESET_ERRNOS:
                        raise ConnectionResetError() from e
                    else:
                        raise

                if not partial:
                    raise ConnectionResetError()

                buffer.write(partial)
                bytes_left -= len(partial)

            return buffer.getvalue()
