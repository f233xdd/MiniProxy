# the part connected with Minecraft
import queue
import socket
import sys
import threading

from . import client, tool


class HostClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], local_port: int, is_crypt: bool, logger):
        super().__init__(server_addr, is_crypt, logger)

        self.local_port = local_port
        self.__virtual_client: socket.socket

    def __connect_local(self):
        """connect with local as a guest"""
        self.__virtual_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__virtual_client.connect((socket.gethostname(), self.local_port))
            self.log.info("local server connected")

        except ConnectionRefusedError:
            self.log.error(f"failed to connect with local server: connection refused")
            raise

    def __send_local_data(self):
        """send data to local"""
        try:
            while True:
                try:
                    data = self._queue_to_local.get(timeout=2)

                except queue.Empty:
                    continue

                self.__virtual_client.sendall(data)

                msg = tool.message(data, client.log_content, client.log_length)
                if msg:
                    self.log.debug(msg)

        except ConnectionError as error:
            self.log.error(f"{error}")

    def __get_local_data(self):
        """get data from local"""
        try:
            while True:
                data = self.__virtual_client.recv(client.MAX_LENGTH)

                self._queue_to_server.put(data)

                msg = tool.message(data, client.log_content, client.log_length)
                if msg:
                    self.log.debug(msg)

        except ConnectionError as error:
            self.log.error(f"{error}")

    def local_client_main(self):
        functions = [self.__send_local_data, self.__get_local_data]

        while True:
            try:
                self.__connect_local()
            except ConnectionRefusedError:
                sys.exit(-1)

            threads = [threading.Thread(target=func, daemon=True) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            self.log.info("connection interrupted")
            self.log.info("reconnecting")
