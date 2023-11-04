# the part connected with a server
import queue
import socket
import logging
import sys
from io import BufferedWriter

from . import tool

MAX_LENGTH: int | None = None

#  log config
log_length: bool | None = None
log_content: bool | None = None
recv_data_log: BufferedWriter | None = None
send_data_log: BufferedWriter | None = None


class Client(object):
    """the part which connected with a server, provide two queues to pass data"""

    def __init__(self, server_addr: tuple[str, int], is_crypt, logger):
        self.log: logging.Logger = logger

        self.server_addr = server_addr
        self.encoding = 'utf_8'
        self.__is_crypt = is_crypt

        self.__server: socket.socket

        self._queue_to_server = queue.Queue()  # for data from local to server
        self._queue_to_local = queue.Queue()  # for data from server to local

        self.__tcp_data_analyser = tool.TCPDataAnalyser()
        self.__tcp_data_packer = tool.TCPDataPacker()
        self.__rsa: tool.RSA | None

        if self.__is_crypt:
            self.__rsa = tool.RSA()  # TODO: RSA cannot work properly
        else:
            self.__rsa = None

        self.__create_socket()

    def __create_socket(self):
        """connect to server"""
        try:
            self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__server.connect(self.server_addr)

            data = self.__server.recv(MAX_LENGTH)
            print(data.decode(self.encoding))

            self.log.info("Connect server")
        except ConnectionError as e:
            self.log.error(e)
            sys.exit(-1)

    def __get_public_key(self):
        pem = self.__server.recv(451)
        print(pem)
        self.__rsa.load_key(pem)
        self.log.debug("load public key")

    def __send_public_key(self):
        pem = self.__rsa.get_public_key()
        self.__server.sendall(pem)
        self.log.debug("send public key")

    def get_server_data(self):
        """get data from server"""
        if self.__rsa:
            self.__send_public_key()

        while True:
            data = self.__server.recv(MAX_LENGTH)

            msg = tool.message(data, log_content, log_length, add_msg="Total")
            if msg:
                self.log.debug(msg)

            self.__tcp_data_analyser.put(data)

            for sorted_data in self.__tcp_data_analyser.packages:
                if self.__rsa:
                    sorted_data = self.__rsa.decrypt(sorted_data)

                self._queue_to_local.put(sorted_data)
                self.log.debug(f"analyse data [{len(sorted_data)}]")

    def send_server_data(self):
        """send data to server"""
        if self.__rsa:
            self.__get_public_key()

        while True:
            data = self._queue_to_server.get()
            if data:
                if self.__rsa:
                    data = self.__rsa.encrypt(data)

                self.__tcp_data_packer.put(data)

                for sorted_data in self.__tcp_data_packer.packages:
                    self.__server.sendall(sorted_data)
                    self.log.debug(f"pack data [{len(sorted_data)}]")

                    msg = tool.message(sorted_data, log_content, log_length)
                    if msg:
                        self.log.debug(msg)
