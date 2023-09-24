# the part connected with Minecraft
import queue
import socket
import threading
import logging

from . import client, logging_ex

log: logging.Logger | None = None


class HostClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], mc_port: int):
        super().__init__(server_addr)

        self._me_port = mc_port
        self._virtual_client: socket.socket
        self._send_func_alive: bool | None = None
        self._get_func_alive: bool | None = None

    def __connect_mc_server(self):
        self._virtual_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._virtual_client.connect((socket.gethostname(), self._me_port))
            log.info("Mc connected")
        except ConnectionError as error:
            log.error(f"Error: failed to connect with mc({error})")
            raise

    def __send_java_data(self):
        """send data to java"""
        self._send_func_alive = True

        try:
            while True:
                try:
                    data = self._data_queue_2.get(timeout=2)

                except queue.Empty:
                    if self._get_func_alive is False:
                        self._send_func_alive = False
                        log.warning("__send_java_data is down for get func(timeout)")
                        break
                    else:
                        continue

                if self._get_func_alive is False:
                    self._send_func_alive = False
                    log.warning("__send_java_data is down for get func")
                    break

                self._virtual_client.sendall(data)

                msg = logging_ex.message(data, client.log_content, client.log_length)
                if msg:
                    log.debug(msg)

        except ConnectionError as error:
            log.error(f"{error} from send_java_data")
            self._send_func_alive = False

    def __get_local_data(self):
        """get data from java"""
        self._get_func_alive = True

        try:
            while True:
                try:
                    data = self._virtual_client.recv(client.MAX_LENGTH)
                except TimeoutError:
                    if self._send_func_alive is False:
                        self._get_func_alive = False
                        log.warning("__get_local_data is down for send func(timeout)")
                        break
                    else:
                        continue

                if self._send_func_alive is False:
                    self._get_func_alive = False
                    log.warning("__get_local_data is down for send func")
                    break

                self._data_queue_1.put(data)

                msg = logging_ex.message(data, client.log_content, client.log_length)
                if msg:
                    log.debug(msg)

        except ConnectionError as error:
            log.error(f"{error} from send_java_data")
            self._get_func_alive = False

    def virtual_client_main(self):
        functions = [self.__send_java_data, self.__get_local_data]

        while True:
            self.__connect_mc_server()

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            log.info("Virtual client is down!")
            input('type [ENTER] to restart> ')
            log.info("Virtual client restart...")
