# the part connected with Minecraft
import queue
import socket
import threading

from . import client, tool


class GuestClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], virtual_server_port: int, is_crypt: bool, log):
        super().__init__(server_addr, is_crypt, log)

        self._port = virtual_server_port
        self._virtual_server: socket.socket
        self._local_client: socket.socket

        self.__init_local_server()

    def __init_local_server(self):
        """initial virtual me server"""
        self._virtual_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._virtual_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ip = socket.gethostbyname(socket.gethostname())
        addr = (ip, self._port)
        self.log.info(f"{ip}:{self._port}\n")

        self._virtual_server.bind(addr)
        self._virtual_server.listen(1)

    def __connect_local(self):
        """connect with local as a server"""
        self._local_client, __ = self._virtual_server.accept()
        self.log.info("local guest connected")

    def __send_local_data(self):
        """send data to local"""
        try:
            while True:
                try:
                    data = self._queue_to_local.get(timeout=2)

                except queue.Empty:
                    continue

                self._local_client.sendall(data)

                msg = tool.message(data, client.log_content, client.log_length)
                if msg:
                    self.log.debug(msg)

        except ConnectionError as error:
            self.log.error(f"{error}")

    def __get_local_data(self):
        """get data from local"""
        try:
            while True:
                data = self._local_client.recv(client.MAX_LENGTH)

                self._queue_to_server.put(data)

                msg = tool.message(data, client.log_content, client.log_length)
                if msg:
                    self.log.debug(msg)

        except ConnectionError as error:
            self.log.error(f"{error}")

    def local_server_main(self):
        functions = [self.__send_local_data, self.__get_local_data]

        while True:
            self.__connect_local()

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            self.log.info("connection interrupted")
            self.log.info("reconnecting")
