import socket

MAX_LENGTH = 4096  # TODO: How much room do we need?


class ClientPort(object):

    def __init__(self, server_host, target_port):
        self.server_addr = (server_host, target_port)

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
            # self._data_queue_2.put(data)
            print(data.decode(self.encoding))

    def send_data(self):
        """send data to server"""
        while True:
            # sent_data = self._data_queue_1.get(block=True)
            sent_data = input('USER@localhost> ')
            self.client.sendall(sent_data.encode(self.encoding))
