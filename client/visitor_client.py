# the part which connected with Minecraft
import socket
import threading
import time

import client

debug: bool = False

_current_time = 0


def ticker(time_break: float) -> bool:
    global _current_time

    if _current_time == 0:
        _current_time = time.time()
        return False
    else:
        current_time_break = time.time() - _current_time
        if current_time_break >= time_break:
            _current_time = time.time()
            return True
        else:
            return False


class VisitClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], virtual_server_port: int):
        super().__init__(server_addr)

        self._port = virtual_server_port
        self._virtual_server: socket.socket
        self._mc_client: socket.socket

        self._send_func_alive = False
        self._get_func_alive = False

        self.__init_virtual_server()

    def __init_virtual_server(self):
        """initial virtual me server"""
        self._virtual_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._virtual_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ip = socket.gethostbyname(socket.gethostname())
        addr = (ip, self._port)
        print(f"{ip}:{self._port}")

        self._virtual_server.bind(addr)
        self._virtual_server.listen(1)

    def __connect_mc_client(self):
        """let mc connect with it as a server"""
        self._mc_client, __ = self._virtual_server.accept()
        print("Mc connected")

    def __send_java_data(self):
        """send data to java"""
        self._send_func_alive = True
        try:
            while True:
                try:
                    data = self._data_queue_2.get(timeout=2)
                except TimeoutError:
                    if not self._get_func_alive:
                        self._send_func_alive = False
                        break
                    else:
                        if ticker(5):
                            self._mc_client.send(b'')
                        continue

                if not self._get_func_alive:
                    self._send_func_alive = False
                    break

                self._mc_client.sendall(data)
                if debug:
                    if data:
                        print("[V]send_java_data: ", data)
        except ConnectionError as error:
            print(f"Error: {error} from send_java_data")
            self._send_func_alive = False

    def __get_local_data(self):
        """get data from java"""
        self._get_func_alive = True
        try:
            while True:
                try:
                    data = self._mc_client.recv(client.MAX_LENGTH)
                except TimeoutError:
                    if not self._send_func_alive:
                        self._get_func_alive = False
                        break
                    else:
                        continue

                if not self._send_func_alive:
                    self._get_func_alive = False
                    break

                self._data_queue_1.put(data)
                if debug:
                    if data:
                        print("[V]get_local_data: ", data)
        except ConnectionError as error:
            print(f"Error: {error} from get_local_data")
            self._get_func_alive = False

    def virtual_server_main(self):
        functions = [self.__send_java_data, self.__get_local_data]
        while True:
            self.__connect_mc_client()
            self._mc_client.settimeout(2)

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            self._mc_client.settimeout(None)
            print("Virtual server is down, restart...")
