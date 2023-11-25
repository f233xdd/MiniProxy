# run this file to start a server
import threading
import time

from server import Server, get_attrs, get_log


def start_server():
    print("[INFO] Initialize ServerPort.", end='... ')
    local_ip, local_ports, max_length = get_attrs()
    log = get_log()

    server_1 = Server(local_ip, local_ports[0], max_length, log)
    server_2 = Server(local_ip, local_ports[1], max_length, log)
    print("Done!")

    print("[INFO] Create processes.", end='... ')
    thd_1 = threading.Thread(target=server_1.start, daemon=True)
    thd_2 = threading.Thread(target=server_2.start, daemon=True)
    print("Done!")

    thd_1.start()
    thd_2.start()
    print("[INFO] Server is running!\n")


def main():
    start_server()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    print("Canceled by [Ctrl-C]")


if __name__ == "__main__":
    main()
