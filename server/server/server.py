# For the server
import queue
import socket
import threading
import logging

from .tool import DoubleQueue, message

# log config
log_length: bool | None = None
log_content: bool | None = None

# main content
MAX_LENGTH: int | None = None


class ClientOffLineError(Exception):
    pass


class Server(object):
    data_queue = DoubleQueue()

    def __init__(self, ip: str, port: int, logger):
        self.log: logging.Logger = logger

        self._extra = {'port': f"{port}"}
        self._port = port  # work as a port and a queue flag

        self.data_queue.add_flag(port)

        self._get_data_alive = None

        self._client: socket.socket | None = None
        self.client_addr: str | None = None

        # initialize server socket
        self._server_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_port.bind((ip, port))
        self._server_port.listen(1)

    def __link_to_client(self):
        """connect to the client"""
        while True:
            client, addr = self._server_port.accept()
            addr = f"{addr[0]}:{addr[1]}"

            self.log.info(f"Accept client. Address: {addr}", extra=self._extra)
            try:
                client.send(
                    f"[THIS IS A TEST MESSAGE]\nWelcome to the proxy server!\nYour internet address: {addr}\n".encode(
                        'utf_8'))
                break

            except ConnectionResetError:
                self.log.warning("[ConnectionResetError] Connection break.", extra=self._extra)

        self._client = client
        self.client_addr = addr

    def __get_data(self):
        """get data from the client and post it into the double queue"""
        self._get_data_alive = True
        self.log.info("Get function start.", extra=self._extra)

        try:
            while True:
                data = self._client.recv(MAX_LENGTH)

                msg = message(data, log_content, log_length)
                if msg:
                    self.log.debug(msg, extra=self._extra)

                if data:
                    self.data_queue.put(data, self._port, exchange=True)

        except ConnectionError as e:
            if e is ConnectionResetError:
                e = "[ConnectionResetError]"
            elif e is ConnectionAbortedError:
                e = "[ConnectionAbortedError]"
            else:
                e = "[ConnectionRefusedError]"

            self.log.warning(f"[{e}] Cancelled ip:{self.client_addr}.", extra=self._extra)
            self._get_data_alive = False

    def __send_data(self):
        """get data from the double queue and send it to the client"""
        self.log.info("Send function start.", extra=self._extra)

        try:
            while True:
                try:
                    data = self.data_queue.get(self._port, timeout=2)
                except queue.Empty:
                    if self._get_data_alive is False:
                        self.log.warning("[TimeoutError] func is down", extra=self._extra)
                        break
                    else:
                        continue

                self._client.sendall(data)

                msg = message(data, log_content, log_length)
                if msg:
                    self.log.debug(msg, extra=self._extra)

        except BrokenPipeError:
            self.log.warning(f"[BrokenPipeError] Cancelled ip:{self.client_addr}.", extra=self._extra)

        except ConnectionError as e:
            if e is ConnectionResetError:
                e = "[ConnectionResetError]"
            elif e is ConnectionAbortedError:
                e = "[ConnectionAbortedError]"
            else:
                e = "[ConnectionRefusedError]"

            self.log.warning(f"[{e}] Cancelled ip:{self.client_addr}.", extra=self._extra)

    def start(self, deque=None):
        if deque:
            self.data_queue = deque

        while True:
            self.__link_to_client()

            threads = [threading.Thread(target=func) for func in [self.__get_data, self.__send_data]]
            self.log.info("Service threads start", extra=self._extra)

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            self.log.info("Service threads terminate", extra=self._extra)
