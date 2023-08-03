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


class HostClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], mc_port: int):
        super().__init__(server_addr)

        self._me_port = mc_port
        self._virtual_client: socket.socket
        self.__send_func_alive = False
        self.__get_func_alive = False

    def __connect_mc_server(self):
        self._virtual_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._virtual_client.connect((socket.gethostname(), self._me_port))
        except ConnectionError as error:
            print(f"Error: failed to connect with mc({error})")
        print("Mc connected")

    def __send_java_data(self):
        """send data to java"""
        self.__send_func_alive = True
        try:
            while True:
                try:
                    data = self._data_queue_2.get(timeout=2)
                except TimeoutError:
                    if not self.__get_func_alive:
                        self.__send_func_alive = False
                        break
                    else:
                        if ticker(5):
                            self._virtual_client.send(b'')
                        continue

                if not self.__get_func_alive:
                    self.__send_func_alive = False
                    break

                self._virtual_client.sendall(data)
                if debug:
                    if data:
                        print("[H]send_java_data: ", data)
        except ConnectionError as error:
            print(f"Error: {error} from send_java_data")
            self.__send_func_alive = False

    def __get_local_data(self):
        """get data from java"""
        self.__get_func_alive = True
        try:
            while True:
                try:
                    data = self._virtual_client.recv(client.MAX_LENGTH)
                except TimeoutError:
                    if not self.__send_func_alive:
                        self.__get_func_alive = False
                        break
                    else:
                        continue

                if not self.__send_func_alive:
                    self.__get_func_alive = False
                    break

                self._data_queue_1.put(data)
                if debug:
                    if data:
                        print("[H]get_local_data: ", data)
        except ConnectionError as error:
            print(f"Error: {error} from get_local_data")
            self.__get_func_alive = False

    def virtual_client_main(self):
        functions = [self.__send_java_data, self.__get_local_data]

        while True:
            self.__connect_mc_server()
            self._virtual_client.settimeout(2)

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            self._virtual_client.settimeout(None)
            print("Virtual client is down!")
            input('type [ENTER] to restart> ')
            print("Virtual client restart...")
