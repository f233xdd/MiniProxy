import queue
import socket
import threading
import time
import logging
import sys
import struct

import buffer

debug: bool = True

MAX_LENGTH: int = -1

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


#  log config
file_log = True

_format_msg = "[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s"
_format_time = "%H:%M:%S"

_formatter = logging.Formatter(_format_msg, _format_time)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
_console_handler.setLevel(logging.INFO)

_log = logging.getLogger("ClientLog")
if debug:
    _log.setLevel(logging.DEBUG)
else:
    _log.setLevel(logging.INFO)
_log.addHandler(_console_handler)


class Client(object):
    """the part which connected with a server, provide two queues to pass data"""
    _data_queue_1 = queue.Queue()  # for data from java to server
    _data_queue_2 = queue.Queue()  # for data from server to java

    def __init__(self, server_addr: tuple[str, int]):
        self.server_addr = server_addr

        self._encoding = 'utf_8'
        self._server: socket.socket

        self._data_buf = buffer.Buffer()
        self._header_buf = buffer.Buffer()
        self._header_buf.set_length(4)

        self._event = threading.Event()
        self._lock = threading.Lock()

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

            if data:
                _log.debug(data)

            while data:
                if len(data) >= 4:
                    if self._data_buf.is_empty and self._data_buf.size == -1:
                        if not self._header_buf.is_empty:
                            data = self._header_buf.put(data, errors="return")
                            self._data_buf.set_length(struct.unpack('i', self._header_buf.get())[0])
                            data = self._data_buf.put(data, errors="return")

                        else:
                            self._data_buf.set_length(struct.unpack('i', data[:4])[0])
                            data = data[4:]
                            data = self._data_buf.put(data, errors="return")

                    else:
                        data = self._data_buf.put(data, errors="return")

                    if self._data_buf.is_full:
                        d = self._data_buf.get(reset_len=True)
                        _log.debug(f"Put {d}")
                        self._data_queue_2.put(d)

                    else:
                        break

                else:
                    if self._data_buf.is_empty and self._data_buf.size == -1:
                        self._header_buf.put(data)
                        data = b''

                    else:
                        data = self._data_buf.put(data, errors="return")

                        if self._data_buf.is_full:
                            d = self._data_buf.get(reset_len=True)
                            _log.debug(f"Put {d}")
                            self._data_queue_2.put(d)

    def send_data(self):
        """send data to server"""
        while True:
            data = self._data_queue_1.get()
            if data:
                self._server.send(struct.pack('i', len(data)))
                self._server.sendall(data)

                _log.debug(data)
