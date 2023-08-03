# the part which connected with Minecraft
import socket

import client

debug: bool = False


class VisitClient(client.Client):

    def __init__(self, server_addr: tuple[str, int], virtual_server_port: int):
        super().__init__(server_addr)

        self._port = virtual_server_port
        self._virtual_server: socket.socket
        self._mc_client: socket.socket

        self.__init_virtual_server()
        self.__connect_mc_client()

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
        print("Mc connected.")

    def send_java_data(self):
        """send data to java"""
        while True:
            data = self._data_queue_2.get()
            self._mc_client.sendall(data)
            if debug:
                if data:
                    print("[V]send_java_data: ", data)

    def get_local_data(self):
        """get data from java"""
        while True:
            data = self._mc_client.recv(client.MAX_LENGTH)
            self._data_queue_1.put(data)
            if debug:
                if data:
                    print("[V]get_local_data: ", data)
