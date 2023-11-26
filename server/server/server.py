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


class ClientOffLineError(Exception):
    pass


class Server(object):
    data_queue = DoubleQueue()

    def __init__(self, ip: str, port: int, max_length: int, log=None):
        self.__extra = {'port': f"{port}"}
        self.__port = port  # work as a port and a queue flag
        self.max_length: int = max_length

        self.data_queue.add_flag(port)

        self.__get_data_alive = None  # provide for send function

        self.__client: socket.socket | None = None
        self.client_addr: str | None = None

        self.log: logging.Logger = log

        # initialize server socket
        self.__server_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server_port.bind((ip, port))
        self.__server_port.listen(1)

    def __link_to_client(self):
        """connect to the client"""
        while True:
            client, addr = self.__server_port.accept()
            addr = f"{addr[0]}:{addr[1]}"
            self.log.info(f"Accept client. Address: {addr}", extra=self.__extra)
            try:
                client.send(
                    f"[THIS IS A TEST MESSAGE]\nWelcome to the proxy server!\nYour internet address: {addr}\n".encode(
                        'utf_8'))
                break

            except ConnectionResetError:
                self.log.warning("[ConnectionResetError] Connection break.", extra=self.__extra)

        self.__client = client
        self.client_addr = addr

    def __get_data(self):
        """get data from the client and post it into the double queue"""
        self.__get_data_alive = True
        self.log.info("Get function start.", extra=self.__extra)

        try:
            while True:
                data = self.__client.recv(self.max_length)

                msg = message(data, log_content, log_length)
                if msg:
                    self.log.debug(msg, extra=self.__extra)

                if data:
                    self.data_queue.put(data, self.__port, exchange=True)
                else:
                    raise ConnectionError

        except ConnectionError as e:
            if e is ConnectionResetError:
                e = "[ConnectionResetError]"
            elif e is ConnectionAbortedError:
                e = "[ConnectionAbortedError]"
            else:
                e = "[ConnectionRefusedError]"

            self.log.warning(f"[{e}] Cancelled ip:{self.client_addr}.", extra=self.__extra)
            self.__get_data_alive = False

    def __send_data(self):
        """get data from the double queue and send it to the client"""
        self.log.info("Send function start.", extra=self.__extra)

        try:
            while True:
                try:
                    data = self.data_queue.get(self.__port, timeout=2)
                except queue.Empty:
                    if self.__get_data_alive is False:
                        self.log.warning("[TimeoutError] func is down", extra=self.__extra)
                        break
                    else:
                        continue

                self.__client.sendall(data)

                msg = message(data, log_content, log_length)
                if msg:
                    self.log.debug(msg, extra=self.__extra)

        except BrokenPipeError:
            self.log.warning(f"[BrokenPipeError] Cancelled ip:{self.client_addr}.", extra=self.__extra)

        except ConnectionError as e:
            if e is ConnectionResetError:
                e = "[ConnectionResetError]"
            elif e is ConnectionAbortedError:
                e = "[ConnectionAbortedError]"
            else:
                e = "[ConnectionRefusedError]"

            self.log.warning(f"[{e}] Cancelled ip:{self.client_addr}.", extra=self.__extra)

    def start(self):
        while True:
            self.__link_to_client()

            threads = [threading.Thread(target=func) for func in [self.__get_data, self.__send_data]]
            self.log.info("Service threads start", extra=self.__extra)

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            self.log.info("Service threads terminate", extra=self.__extra)
