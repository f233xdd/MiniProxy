#  run this file to start a server
import threading
import json

import server

server_ip: str = ""
open_ports: list = []


def init():
    global open_ports, server_ip
    #  load json file
    json_file = open("config.json")
    config = json.load(json_file)
    #  quick set up
    server.MAX_LENGTH = config["data_max_length"]
    server_ip = config["local_address"]["private_ip"]
    open_ports = config["local_address"]["ports"]
    server.file_log = config["file_log"]
    server.debug = config["debug"]["global"]
    server.log_length = config["debug"]["length"]
    server.log_context = config["debug"]["context"]


def main():
    init()

    print("Initialize ServerPort.", end='... ')
    server_1 = server.Server(server_ip, open_ports[0])
    server_2 = server.Server(server_ip, open_ports[1])
    print("Done!")

    print("Create threads.", end='... ')
    thread_1 = threading.Thread(target=server_1.start)
    thread_2 = threading.Thread(target=server_2.start)
    print("Done!")

    thread_1.start()
    thread_2.start()
    print("Server running!\n")


if __name__ == "__main__":
    main()
