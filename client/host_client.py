# the part which connected with Minecraft
import socket
import threading

import client

debug: bool = False


class HostClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], mc_port: int):
        super().__init__(server_addr)

        self._me_port = mc_port
        self._virtual_client: socket.socket

    def __connect_mc_server(self):
        self._virtual_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._virtual_client.connect((socket.gethostname(), self._me_port))
        except ConnectionError as error:
            print(f"Error: failed to connect with mc({error})")
        print("Mc connected")

    def __send_java_data(self):
        """send data to java"""
        try:
            while True:
                data = self._data_queue_2.get()
                self._virtual_client.sendall(data)
                if debug:
                    if data:
                        print("[H]send_java_data: ", data)
        except ConnectionError as error:
            print(f"Error: {error} from send_java_data")

    def __get_local_data(self):
        """get data from java"""
        try:
            while True:
                data = self._virtual_client.recv(client.MAX_LENGTH)
                self._data_queue_1.put(data)
                if debug:
                    if data:
                        print("[H]get_local_data: ", data)
        except ConnectionError as error:
            print(f"Error: {error} from get_local_data")

    def virtual_client_main(self):
        functions = [self.__send_java_data, self.__get_local_data]

        while True:
            self.__connect_mc_server()

            threads = [threading.Thread(target=func) for func in functions]

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            print("Virtual client is down!")
            input('type [ENTER] to restart> ')
            print("Virtual client restart...")
