# the part connected with a server
import queue
import socket
import logging
import sys
from io import BufferedWriter

import client
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

    def __init__(self, server_addr: tuple[str, int]):
        self.server_addr = server_addr
        self.encoding = 'utf_8'

        self.__server: socket.socket

        self._queue_to_server = queue.Queue()  # for data from local to server
        self._queue_to_local = queue.Queue()  # for data from server to local

        self.__tcp_data_analyser = tool.TCPDataAnalyser()
        self.__tcp_data_packer = tool.TCPDataPacker()

        if client.conf["crypt"] and tool.crypt_available:
            __rsa = tool.RSA()  # TODO: get public key and encrypt data
        else:
            __rsa = None

        self.__create_socket()

    def __create_socket(self):
        """connect to server"""
        try:
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.connect(self.server_addr)

            data = self.__server.recv(MAX_LENGTH)
            print(data.decode(self.encoding))

            log.info("Connect server.")
        except ConnectionError as e:
            log.error(e)
            sys.exit(-1)

    def get_server_data(self):
        """get data from server"""
        while True:
            data = self.__server.recv(MAX_LENGTH)

            msg = tool.message(data, log_content, log_length, add_msg="Total")
            if msg:
                log.debug(msg)

            self.__tcp_data_analyser.put(data)

            for sorted_data in self.__tcp_data_analyser.packages:
                self._queue_to_local.put(sorted_data)
                log.debug(f"analyse data [{len(sorted_data)}]")

                # recv_data_log.write(sorted_data)
                # recv_data_log.write(b'\n')

    def send_server_data(self):
        """send data to server"""
        while True:
            data = self._queue_to_server.get()
            if data:
                self.__tcp_data_packer.put(data)

                for sorted_data in self.__tcp_data_packer.packages:
                    log.debug(f"pack data [{len(sorted_data)}]")
                    self.__server.sendall(sorted_data)

                    msg = tool.message(sorted_data, log_content, log_length)
                    if msg:
                        log.debug(msg)

                    # send_data_log.write(sorted_data)
                    # send_data_log.write(b'\n')
