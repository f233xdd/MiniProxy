# the part connected with a server
import queue
import socket
import logging
import struct
from io import BufferedWriter

import buffer
import logging_ex

MAX_LENGTH: int | None = None

#  log config
log_length: bool | None = None
log_context: bool | None = None
log: logging.Logger | None = None
recv_data_log: BufferedWriter | None = None
send_data_log: BufferedWriter | None = None


class Client(object):
    """the part which connected with a server, provide two queues to pass data"""
    _data_queue_1 = queue.Queue()  # for data from java to server
    _data_queue_2 = queue.Queue()  # for data from server to java

    def __init__(self, server_addr: tuple[str, int]):
        self.server_addr = server_addr

        self._encoding = 'utf_8'
        self._server: socket.socket

        self._data_buf = buffer.Buffer()
        self._header_buf = buffer.Buffer(static=True, max_size=4)

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

            logging_ex.log_debug_msg(data, log, log_context, log_length, add_msg="All")

            recv_data_log.write(data)
            recv_data_log.write(b'\n')

            while data:
                if len(data) >= 4:
                    if self._data_buf.is_empty and self._data_buf.size == -1:
                        if not self._header_buf.is_empty:
                            data = self._header_buf.put(data, errors="return")

                            length = struct.unpack('i', data[:4])[0]
                            self._data_buf.set_length(length)
                            log.debug(f"Set length: {length}")

                            data = self._data_buf.put(data, errors="return")

                        else:
                            length = struct.unpack('i', data[:4])[0]
                            self._data_buf.set_length(length)
                            log.debug(f"Set length: {length}")

                            data = data[4:]
                            data = self._data_buf.put(data, errors="return")

                    else:
                        data = self._data_buf.put(data, errors="return")

                    if self._data_buf.is_full:
                        d = self._data_buf.get(reset_len=True)

                        logging_ex.log_debug_msg(d, log, log_context, log_length, add_msg="Put")

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

                            logging_ex.log_debug_msg(d, log, log_context, log_length, add_msg="Put")

                            self._data_queue_2.put(d)

    def send_data(self):
        """send data to server"""
        while True:
            data = self._data_queue_1.get()
            if data:
                data = b"".join([struct.pack('i', len(data)), data])
                self._server.sendall(data)

                logging_ex.log_debug_msg(data, log, log_context, log_length)

                send_data_log.write(data)
                send_data_log.write(b'\n')
