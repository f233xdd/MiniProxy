# run this file to start a server
import multiprocessing
import time

from server import *


def start_server():
    print("[INFO] Initialize ServerPort.", end='... ')
    server_1 = Server(local_ip, local_ports[0], log)
    server_2 = Server(local_ip, local_ports[1], log)
    print("Done!")

    print("[INFO] Create processes.", end='... ')
    process_1 = multiprocessing.Process(target=server_1.start, args=(server_1.data_queue,))
    process_2 = multiprocessing.Process(target=server_2.start, args=(server_2.data_queue,))
    print("Done!")

    process_1.start()
    process_2.start()
    print("[INFO] Server is running!\n")

    return [process_1, process_2]


def main():
    prc = start_server()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        for p in prc:
            p.terminate()

    print("Canceled by [Ctrl-C]")


if __name__ == "__main__":
    main()
