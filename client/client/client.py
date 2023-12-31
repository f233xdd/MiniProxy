# the part connected with a server
import queue
import socket
import logging
import sys
import threading
import typing
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
        self.encoding: str = 'utf_8'
        self.__is_crypt: bool = is_crypt

        self.__server: socket.socket

        self._queue_to_server = queue.Queue()  # for data from local to server
        self._queue_to_local = queue.Queue()  # for data from server to local

        self.__tcp_data_analyser = tool.TCPDataAnalyser()
        self.__tcp_data_packer = tool.TCPDataPacker()
        self.__rsa: tool.RSA | None
        self.__cipher: tool.Cipher | None

        if self.__is_crypt:
            self.__rsa = tool.RSA()  # TODO: RSA cannot work properly
            self.__cipher = tool.Cipher()
            self.__got_public_key = threading.Event()

        else:
            self.__rsa = None
            self.__cipher = None

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

    def __get_key(self):
        pem = next(self.__recv())
        print(pem)
        self.__rsa.load_key(pem)
        self.log.info("load public key")
        self.__got_public_key.set()

        d = next(self.__recv())
        print(d)
        key = self.__rsa.decrypt(d)
        self.__cipher.load_key(key)
        self.log.info("load cipher")

    def __send_key(self):
        pem = self.__rsa.get_public_key()
        self.__send(pem)
        self.log.info("send public key")

        self.__got_public_key.wait()
        key = self.__rsa.encrypt(self.__cipher.encrypt_key)
        self.__send(key)
        self.log.info("send cipher")

    def __recv(self) -> typing.Iterator[bytes]:
        try:
            data = self.__server.recv(MAX_LENGTH)
        except ConnectionError as e:
            self.log.error(e)
            sys.exit(-1)

        msg = tool.message(data, log_content, log_length, add_msg="Total")
        if msg:
            self.log.debug(msg)

        self.__tcp_data_analyser.put(data)
        for sorted_data in self.__tcp_data_analyser.packages:
            self.log.debug(f"analyse data [{len(sorted_data)}]")
            yield sorted_data

    def __send(self, data: bytes):
        self.__tcp_data_packer.put(data)
        for sorted_data in self.__tcp_data_packer.packages:
            self.log.debug(f"pack data [{len(sorted_data)}]")

            try:
                self.__server.sendall(sorted_data)
            except ConnectionError as e:
                self.log.error(e)
                sys.exit(-1)

            msg = tool.message(data, log_content, log_length)
            if msg:
                self.log.debug(msg)

    def get_server_data(self):
        """get data from server"""
        if self.__is_crypt:
            self.__send_key()

        while True:
            for data in self.__recv():
                if self.__cipher:
                    data = self.__cipher.decrypt(data)

                self._queue_to_local.put(data)

    def send_server_data(self):
        """send data to server"""
        if self.__is_crypt:
            self.__get_key()

        while True:
            data = self._queue_to_server.get()
            if data:
                if self.__cipher:
                    data = self.__cipher.encrypt(data)

                self.__send(data)
