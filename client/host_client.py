# the part which connected with Minecraft
import socket

import client

debug: bool = False


class HostClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], mc_port: int):
        super().__init__(server_addr)

        self._me_port = mc_port
        self._virtual_client: socket.socket

        self.__init_virtual_client()
        self.__connect_mc_server()

    def __init_virtual_client(self):
        self._virtual_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __connect_mc_server(self):
        self._virtual_client.connect((socket.gethostname(), self._me_port))
        print("Mc connected.")

    def send_java_data(self):
        """send data to java"""
        while True:
            data = self._data_queue_2.get()
            self._virtual_client.sendall(data)
            if debug:
                if data:
                    print("[H]send_java_data: ", data)

    def get_local_data(self):
        """get data from java"""
        while True:
            data = self._virtual_client.recv(client.MAX_LENGTH)
            self._data_queue_1.put(data)
            if debug:
                if data:
                    print("[H]get_local_data: ", data)
