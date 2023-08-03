import queue
import socket
import time

MAX_LENGTH = 4096  # TODO: How much room do we need?


class Port(object):
    _data_queue_1 = queue.Queue()  # for data from java to server
    _data_queue_2 = queue.Queue()  # for data from server to java


class ClientPort(Port):

    def __init__(self, server_host, target_port):
        self.server_addr = (server_host, target_port)

        self._port = target_port
        self.encoding = 'utf_8'
        self.client: socket.socket

        self.__create_socket()

    def __create_socket(self):
        """connect to server"""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.server_addr)

        data = self.client.recv(MAX_LENGTH)
        print(data.decode(self.encoding))

    def get_data(self):
        """get data from server"""
        while True:
            data = self.client.recv(MAX_LENGTH)
            print(data.decode(self.encoding))

    def send_data(self):
        """send data to server"""
        for i in range(25):
            sent_data = f"[{self._port}] Data({i})"
            self.client.sendall(sent_data.encode(self.encoding))
            time.sleep(0.5)
