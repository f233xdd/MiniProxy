# import socket
import threading

from test_client import ClientPort


def main(address, target_port):
    client = ClientPort(address, target_port)
    threads = [threading.Thread(target=func) for func in [client.get_data, client.send_data]]

    for thd in threads:
        thd.start()

    for thd in threads:
        thd.join()


if __name__ == '__main__':
    serverport = int(input("Server port: "))

    main("62.234.42.66", serverport)
