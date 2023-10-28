# run this file to start a server
import multiprocessing

from server import *


def main():
    print("Initialize ServerPort.", end='... ')
    server_1 = Server(local_addr[0], local_addr[1][0])
    server_2 = Server(local_addr[0], local_addr[1][1])
    print("Done!")

    print("Create threads.", end='... ')
    thread_1 = multiprocessing.Process(target=server_1.start, args=(server_1.data_queue,))
    thread_2 = multiprocessing.Process(target=server_2.start, args=(server_2.data_queue,))
    print("Done!")  # rebuild with process

    thread_1.start()
    thread_2.start()
    print("Server is running!\n")

    thread_1.join()
    thread_2.join()


if __name__ == "__main__":
    main()
