# run this file to start host client
import threading
import json

import host_client
import client

server_addr: tuple[str, int] = ('', -1)


def init():
    """set up basic config"""
    global server_addr

    file = open("config.json")
    host_config = json.load(file)["host"]

    client.MAX_LENGTH = host_config["data_max_length"]
    addr = host_config["server_address"]
    server_addr = addr["internet_ip"], addr["port"]
    client.file_log = host_config["file_log"]
    client.debug = host_config["debug"]
    client.file_log = host_config["file_log"]


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
