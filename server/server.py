# For the server
import queue
import socket
import sys
import threading
import time
import logging

import queue_ex

#  log config
format_msg = "[%(levelname)s] [%(asctime)s] [%(ip)s] [%(funcName)s] %(message)s"
format_time = "%H:%M:%S"

formatter = logging.Formatter(format_msg, format_time)


class ErrorFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        if record.__dict__["levelname"] == "ERROR":
            return False
        else:
            return True


log_filter = ErrorFilter()

file_handler = logging.FileHandler("ServerLog.log", mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

log = logging.getLogger("ServerLog")
log.addHandler(file_handler)
log.addHandler(console_handler)
log.addFilter(log_filter)

#  main context
MAX_LENGTH = 4096  # TODO: How much room do we need?


class ClientOffLineError(Exception):
    pass


class ServerPort(object):
    _queue = queue_ex.DoubleQueue()

    def __init__(self, host: str, port: int, mode=None):
        # TODO: tomorrow we'll add the function about the arg 'mode'

        self.ip = {'ip': f"{host}:{port}"}
        self._port = port
        self._cache = []  # store data which is not sent

        self._queue.add_sign(port)

        self._data_queue = queue.Queue()

        self._get_func = False
        self._send_func = False

        self._client: socket.socket | None = None
        self.client_addr: tuple | None = None
        self._to_client: socket.socket | None = None

        # initialize server socket
        self.server_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_port.bind((host, port))
        self.server_port.listen(2)

    def __link_to_client(self):
        """connect to the client"""
        while True:
            client, addr = self.server_port.accept()
            addr = f"{addr[0]}:{addr[1]}"

            log.info(f"Accept client. Address: {addr}", extra=self.ip)
            try:
                client.sendall(f"Welcome to the server!\nAddress: {addr}\n".encode('utf_8'))
                break

            except ConnectionResetError:
                log.warning("Client off-line, connection break.", extra=self.ip)

        self._client = client
        self.client_addr = addr

        self._queue.put(self._client, self._port)

    def __get_to_client(self):
        while True:
            try:
                self._to_client = self._queue.get(self._port, timeout=3)
                break

            except (TimeoutError, queue.Empty):  # avoid a client is not alive, to_client has not linked
                # and it is stuck forever
                if not self._get_func:  # when get function is not running, which means the client is not alive
                    raise ClientOffLineError  # break the loop to stop sticking the whole thread

    def __get_data(self):
        """get data from the client and post it into a queue"""
        self._get_func = True
        try:
            while True:
                data = self._client.recv(MAX_LENGTH)
                self._data_queue.put(data)

        except ConnectionResetError:
            log.warning(f"Cancelled ip:{self.client_addr}.", extra=self.ip)
            self._get_func = False

    def __send_data(self):
        """get data from queue and send it to the other client"""
        self._send_func = False
        try:
            while True:
                if self._cache:
                    data = self._cache.pop()
                else:
                    data = self._data_queue.get()

                    self._to_client.sendall(data)  # FIXME: BrokenPipeError will be raised, stop it!

        except BrokenPipeError as error:
            self._cache.append(data)  # No, it won't unless you say so.
            log.warning(error, extra=self.ip)

        except ConnectionResetError:
            log.warning(f"Cancelled ip:{self.client_addr}.", extra=self.ip)
            self._send_func = False

    def start(self):
        while True:
            if not self._get_func:
                self.__link_to_client()
                thread = threading.Thread(target=self.__get_data)
                thread.start()

                log.info("Get function start.", extra=self.ip)

            if not self._send_func:
                try:
                    self.__get_to_client()
                except ClientOffLineError:
                    log.warning("Client off line, continue.", extra=self.ip)
                    continue  # back to the origin

                thread = threading.Thread(target=self.__send_data)
                thread.start()

                log.info("Send function start.", extra=self.ip)

            while self._get_func and self._send_func:
                time.sleep(0.001)
