import socket

import client


debug = False


class VisitClient(client.Client):

    def __init__(self, server_addr, virtual_server_port: int):
        super().__init__(server_addr)
        self._port = virtual_server_port
        self._mc_client: socket.socket

        self.__create_fake_server()

    def __create_fake_server(self):
        """let mc connect with it as a server"""
        fake_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fake_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ip = socket.gethostbyname(socket.gethostname())
        addr = (ip, self._port)
        print(f"{ip}:{self._port}")

        fake_server.bind(addr)
        fake_server.listen(1)

        mc, __ = fake_server.accept()
        print("Mc connected.")
        self._mc_client = mc

    def send_java_data(self):
        """send data to java"""
        while True:
            data = self._data_queue_2.get()
            self._mc_client.sendall(data)
            print("[V]send_java_data: ", data)

    def get_local_data(self):
        """get data from java"""
        while True:
            data = self._mc_client.recv(client.MAX_LENGTH)
            self._data_queue_1.put(data)
            if data:
                print("[V]get_local_data: ", data)
