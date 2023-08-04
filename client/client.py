# the part which connected with a server
import queue
import socket
import time

MAX_LENGTH: int = 0

_current_time = 0


def ticker(time_break: float) -> bool:
    global _current_time

    if _current_time == 0:
        _current_time = time.time()
        return False
    else:
        current_time_break = time.time() - _current_time
        if current_time_break >= time_break:
            _current_time = time.time()
            return True
        else:
            return False


class Client(object):
    _data_queue_1 = queue.Queue()  # for data from java to server
    _data_queue_2 = queue.Queue()  # for data from server to java

    def __init__(self, server_addr: tuple[str, int]):
        self.server_addr = server_addr

        self._encoding = 'utf_8'
        self._server: socket.socket

        self.__create_socket()

    def __create_socket(self):
        """connect to server"""
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect(self.server_addr)

        data = self._server.recv(MAX_LENGTH)
        print(data.decode(self._encoding))

    def get_data(self):
        """get data from server"""
        while True:
            data = self._server.recv(MAX_LENGTH)
            if data == b'\x00':
                continue
            self._data_queue_2.put(data)

    def send_data(self):
        """send data to server"""
        while True:
            sent_data = self._data_queue_1.get()
            self._server.sendall(sent_data)
