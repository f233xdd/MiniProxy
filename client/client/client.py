# the part connected with a server
import queue
import socket
import logging
import struct
from io import BufferedWriter

from . import tool

MAX_LENGTH: int | None = None

#  log config
log_length: bool | None = None
log_content: bool | None = None
log: logging.Logger | None = None
recv_data_log: BufferedWriter | None = None
send_data_log: BufferedWriter | None = None


class Client(object):
    """the part which connected with a server, provide two queues to pass data"""
    _queue_to_server = queue.Queue()  # for data from local to server
    _queue_to_local = queue.Queue()  # for data from server to local

    def __init__(self, server_addr: tuple[str, int]):
        self.server_addr = server_addr

        self._encoding = 'utf_8'
        self._server: socket.socket

        self._data_buf = tool.BinaryBuffer()
        self._header_buf = tool.BinaryBuffer(static=True, size=4)

        self.__create_socket()

    def __create_socket(self):
        """connect to server"""
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.connect(self.server_addr)

        data = self._server.recv(MAX_LENGTH)
        print(data.decode(self._encoding))

        log.info("Connect server.")

    def get_server_data(self):
        """get data from server"""
        while True:
            data = self._server.recv(MAX_LENGTH)

            msg = tool.message(data, log_content, log_length, add_msg="All")
            if msg:
                log.debug(msg)

            # recv_data_log.write(data)
            # recv_data_log.write(b'\n')

            while data:
                if len(data) >= 4:
                    if self._data_buf.is_empty and self._data_buf.size is None:
                        if not self._header_buf.is_empty:
                            data = self._header_buf.put(data, errors="return")

                            length = struct.unpack('i', data[:4])[0]
                            self._data_buf.set_size(length)
                            log.debug(f"Set length: {length}")

                            data = self._data_buf.put(data, errors="return")

                        else:
                            length = struct.unpack('i', data[:4])[0]
                            self._data_buf.set_size(length)
                            log.debug(f"Set length: {length}")

                            data = data[4:]
                            data = self._data_buf.put(data, errors="return")

                    else:
                        data = self._data_buf.put(data, errors="return")

                    if self._data_buf.is_full:
                        sorted_data = self._data_buf.get(reset_size=True)

                        msg = tool.message(sorted_data, log_content, log_length, add_msg="Put")
                        if msg:
                            log.debug(msg)

                        self._queue_to_local.put(sorted_data)

                    else:
                        break

                else:
                    if self._data_buf.is_empty and self._data_buf.size is None:
                        self._header_buf.put(data)
                        data = b''

                    else:
                        data = self._data_buf.put(data, errors="return")

                        if self._data_buf.is_full:
                            sorted_data = self._data_buf.get(reset_size=True)

                            msg = tool.message(sorted_data, log_content, log_length, add_msg="Put")
                            if msg:
                                log.debug(msg)

                            self._queue_to_local.put(sorted_data)

    def send_server_data(self):
        """send data to server"""
        while True:
            data = self._queue_to_server.get()
            if data:
                data = b"".join([struct.pack('i', len(data)), data])
                self._server.sendall(data)

                msg = tool.message(data, log_content, log_length)
                if msg:
                    log.debug(msg)

                # send_data_log.write(data)
                # send_data_log.write(b'\n')
