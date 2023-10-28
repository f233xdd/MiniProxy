# the part connected with Minecraft
import queue
import socket
import threading
import logging

from . import client, tool

log: logging.Logger | None = None


class HostClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], mc_port: int):
        super().__init__(server_addr)

        self.local_port = mc_port
        self.__virtual_client: socket.socket
        # self._send_func_alive: bool | None = None
        # self._get_func_alive: bool | None = None

    def __connect_local(self):
        """connect with local as a guest"""
        self.__virtual_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__virtual_client.connect((socket.gethostname(), self.local_port))
            log.info("local server connected")
        except ConnectionError as error:
            log.error(f"failed to connect with local server: {error}")
            raise

    def __send_local_data(self):
        """send data to local"""
        # self._send_func_alive = True

        try:
            while True:
                try:
                    data = self._queue_to_local.get(timeout=2)

                except queue.Empty:
                    continue
                    # if self._get_func_alive is False:
                    #     self._send_func_alive = False
                    #     log.warning("interrupt for get func(timeout)")
                    #     break
                    # else:
                    #     continue

                # if self._get_func_alive is False:
                #     self._send_func_alive = False
                #     log.warning("interrupt for get func")
                #     break

                self.__virtual_client.sendall(data)

                msg = tool.message(data, client.log_content, client.log_length)
                if msg:
                    log.debug(msg)

        except ConnectionError as error:
            log.error(f"{error}")
            # self._send_func_alive = False

    def __get_local_data(self):
        """get data from local"""
        # self._get_func_alive = True

        try:
            while True:
                try:
                    data = self.__virtual_client.recv(client.MAX_LENGTH)
                except TimeoutError:
                    continue
                    # if self._send_func_alive is False:
                    #     self._get_func_alive = False
                    #     log.warning("interrupt for send func(timeout)")
                    #     break
                    # else:
                    #     continue

                # if self._send_func_alive is False:
                #     self._get_func_alive = False
                #     log.warning("interrupt for send func")
                #     break

                self._queue_to_server.put(data)

                msg = tool.message(data, client.log_content, client.log_length)
                if msg:
                    log.debug(msg)

        except ConnectionError as error:
            log.error(f"{error}")
            # self._get_func_alive = False

    def local_client_main(self):
        functions = [self.__send_local_data, self.__get_local_data]

        while True:
            self.__connect_local()

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            log.info("connection interrupted")
            log.info("reconnecting")
