#  run this file to start a server
import threading
import json

import server
import logging_ex

server_ip: str = ""
open_ports: list = []


def init():
    global open_ports, server_ip
    #  load json file
    json_file = open("config.json")
    config = json.load(json_file)
    # set up
    server.MAX_LENGTH = config["data_max_length"]
    server_ip = config["local_address"]["private_ip"]
    open_ports = config["local_address"]["ports"]
    # init log settings
    if config["file_log"]:
        server._log = logging_ex.create_logger("Server", "server.log")
    else:
        server._log = logging_ex.create_logger("Sever")

    server.log_length = config["console"]["length"]
    server.log_context = config["console"]["context"]


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
