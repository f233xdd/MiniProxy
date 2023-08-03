import queue
import socket
import threading

from client import ClientPort, MAX_LENGTH


class SelfClient(ClientPort):

    def __init__(self, host, port):
        super().__init__(host, port)
        self._data_queue = queue.Queue()

    def get_data(self):
        while True:
            data = self.client.recv(MAX_LENGTH)
            self._data_queue.put(data)

    def reflect_msg(self):
        reflect_port = 2000

        reflect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        reflect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        reflect_sock.bind((socket.gethostname(), reflect_port))
        reflect_sock.listen(2)
        while True:
            client, __ = reflect_sock.accept()

            try:
                while True:
                    data = self._data_queue.get()
                    client.sendall(data)
            except ConnectionResetError:
                print("Listener off-line.")


def main(host, port):
    client = SelfClient(host, port)

    threads = [threading.Thread(target=func) for func in [client.get_data, client.send_data, client.reflect_msg]]

    for thd in threads:
        thd.start()


if __name__ == '__main__':
    main("62.234.42.66", 25566)
