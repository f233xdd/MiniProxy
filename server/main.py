#  run this file to start a server
import threading
import json

import server

server_host: str = ""
open_ports: list = []


def init():
    global open_ports, server_host
    #  load json file
    json_file = open("config.json")
    config = json.load(json_file)
    #  quick set up
    server.MAX_LENGTH = config["data_max_length"]
    server_host = config["server_host"]
    open_ports = config["ports"]
    server.file_log = config["file_log"]


def main():
    init()

    print("Initialize ServerPort.", end='... ')
    server_1 = server.Server(server_host, open_ports[0])
    server_2 = server.Server(server_host, open_ports[1])
    print("Done!")

    print("Create threads.", end='... ')
    thread_1 = threading.Thread(target=server_1.start)
    thread_2 = threading.Thread(target=server_2.start)
    check_thread = [threading.Thread(target=func) for func in
                    [server_1.check_client_alive, server_2.check_client_alive]]
    print("Done!")

    thread_1.start()
    thread_2.start()
    for thread in check_thread:
        thread.start()
    print("Server running!\n")


if __name__ == "__main__":
    main()
