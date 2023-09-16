import queue
import socket
import logging
import struct

import buffer

MAX_LENGTH: int = -1

#  log config
log_length = None
log_context = None
log: logging.Logger | None = None


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

            if data:
                msg = ""
                if log_length:
                    msg = "".join([msg, f"[{len(data)}]"])
                if log_context:
                    if msg:
                        msg = "".join([msg, ' ', str(data)])
                    else:
                        msg = data
                if msg:
                    log.debug(f"All {msg}")

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

                        if data:
                            msg = ""
                            if log_length:
                                msg = "".join([msg, f"[{len(data)}]"])
                            if log_context:
                                if msg:
                                    msg = "".join([msg, ' ', str(data)])
                                else:
                                    msg = data
                            if msg:
                                log.debug(f"Put {msg}")

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

                            if data:
                                msg = ""
                                if log_length:
                                    msg = "".join([msg, f"[{len(data)}]"])
                                if log_context:
                                    if msg:
                                        msg = "".join([msg, ' ', str(data)])
                                    else:
                                        msg = data
                                if msg:
                                    log.debug(f"Put {msg}")

                            self._data_queue_2.put(d)

    def send_data(self):
        """send data to server"""
        while True:
            data = self._data_queue_1.get()
            if data:
                self._server.send(struct.pack('i', len(data)))
                self._server.sendall(data)

                if data:
                    msg = ""
                    if log_length:
                        msg = "".join([msg, f"[{len(data)}]"])
                    if log_context:
                        if msg:
                            msg = "".join([msg, ' ', str(data)])
                        else:
                            msg = data
                    if msg:
                        log.debug(msg)
