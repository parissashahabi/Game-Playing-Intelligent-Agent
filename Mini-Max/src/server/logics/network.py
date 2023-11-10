import socket


class Socket:

    def __init__(self, connection: socket.socket, address=None):
        self._connection = connection
        self.addr = address

    @staticmethod
    def create(ip, port):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind((ip, port))
        return Socket(connection)

    def set_time_out(self, timeout):
        self._connection.settimeout(timeout)

    def accept_client(self):
        self._connection.listen()
        client, addr = self._connection.accept()
        return Socket(client, addr)

    def read_utf(self):
        # length = struct.unpack('>H', self._connection.recv(2))[0]
        data = self._connection.recv(2048).decode('utf-8').strip()
        return data

    def write_utf(self, msg: str):
        # self._connection.send(struct.pack('>H', len(str(msg))))
        self._connection.send(str(msg+"\n").encode('utf-8'))

    def read_data(self):
        try:
            return self.read_utf().strip()
        except Exception as e:
            return None
