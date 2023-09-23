# the part connected with Minecraft
import queue
import socket
import threading
import logging

import client
import logging_ex

log: logging.Logger | None = None


class VisitClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], virtual_server_port: int):
        super().__init__(server_addr)

        self._port = virtual_server_port
        self._virtual_server: socket.socket
        self._mc_client: socket.socket

        self._send_func_alive: bool | None = None
        self._get_func_alive: bool | None = None

        self.__init_virtual_server()

    def __init_virtual_server(self):
        """initial virtual me server"""
        self._virtual_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._virtual_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ip = socket.gethostbyname(socket.gethostname())
        addr = (ip, self._port)
        print(f"{ip}:{self._port}\n")

        self._virtual_server.bind(addr)
        self._virtual_server.listen(1)

    def __connect_mc_client(self):
        """let mc connect with it as a server"""
        self._mc_client, __ = self._virtual_server.accept()
        log.info("Mc connected")

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

                self._mc_client.sendall(data)

                msg = logging_ex.debug_msg(data, client.log_content, client.log_length)
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
                    data = self._mc_client.recv(client.MAX_LENGTH)
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

                msg = logging_ex.debug_msg(data, client.log_content, client.log_length)
                if msg:
                    log.debug(msg)

        except ConnectionError as error:
            log.error(f"{error} from send_java_data")
            self._get_func_alive = False

    def virtual_server_main(self):
        functions = [self.__send_java_data, self.__get_local_data]

        while True:
            self.__connect_mc_client()

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            log.info("Virtual server is down, restart...")
