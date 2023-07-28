import threading

from server import ServerPort


def main(server_host: str, ports: tuple):
    print("Initialize ServerPort.", end='... ')
    server_port_1 = ServerPort(server_host, ports[0])
    server_port_2 = ServerPort(server_host, ports[1])
    print("Done!")

    print("Create threads.", end='... ')
    thread_1 = threading.Thread(target=server_port_1.start)
    thread_2 = threading.Thread(target=server_port_2.start)
    print("Done!")

    thread_1.start()
    thread_2.start()
    print("Server running!\n")


if __name__ == "__main__":
    main('', (25565, 25566,))
