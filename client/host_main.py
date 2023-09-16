# run this file to start host client
import threading
import json

import host_client
import client

import logging_ex

server_addr: tuple[str, int] = ('', -1)


def init():
    """set up basic config"""
    global server_addr

    file = open("config.json")
    config = json.load(file)["host"]

    client.MAX_LENGTH = config["data_max_length"]
    addr = config["server_address"]
    server_addr = addr["internet_ip"], addr["port"]

    if config["file_log"]:
        client._log = logging_ex.create_logger("Host", "host.log")
    else:
        client._log = logging_ex.create_logger("Host")

    client.log_length = config["console"]["length"]
    client.log_context = config["console"]["context"]

def main():
    init()

    mc_open_port = int(input("Mc local port: "))
    host = host_client.HostClient(server_addr, mc_open_port)

    functions = [host.send_data, host.get_data, host.virtual_client_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
