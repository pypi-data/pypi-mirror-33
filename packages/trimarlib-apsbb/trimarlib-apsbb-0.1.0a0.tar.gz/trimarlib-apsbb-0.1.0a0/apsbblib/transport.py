import socket
from erpc import transport


class SocketTransport(transport.FramedTransport):
    def __init__(self, sock):
        super().__init__()
        self._sock = sock

    def _base_send(self, data):
        try:
            self._sock.sendall(data)
        except Exception as e:
            raise transport.ConnectionClosed from e

    def _base_receive(self, count):
        buf = b''
        while count:
            try:
                tmp = self._sock.recv(count)
            except Exception as e:
                raise transport.ConnectionClosed from e
            if tmp == b'':
                raise transport.ConnectionClosed()
            buf += tmp
            count -= len(tmp)
        return buf
