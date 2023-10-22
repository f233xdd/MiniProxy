# run this file to start a server
import threading

from server import *


def main():
    print("Initialize ServerPort.", end='... ')
    server_1 = Server(local_addr[0], local_addr[1][0])
    server_2 = Server(local_addr[0], local_addr[1][1])
    print("Done!")

    print("Create threads.", end='... ')
    thread_1 = threading.Thread(target=server_1.start)
    thread_2 = threading.Thread(target=server_2.start)
    print("Done!")  # rebuild with process

    thread_1.start()
    thread_2.start()
    print("Server is running!\n")


if __name__ == "__main__":
    main()
