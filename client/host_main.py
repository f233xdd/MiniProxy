# run this file to start host client
import threading
import json

from client import logging_ex, host_client, client

server_addr: tuple[str | None, int | None] = (None, None)


def init():
    """set up basic config"""
    global server_addr

    file = open("client/config.json")
    config = json.load(file)["host"]

    client.MAX_LENGTH = config["data_max_length"]
    addr = config["server_address"]
    server_addr = addr["internet_ip"], addr["port"]

    if config["debug"]["file_log"]:
        logger = logging_ex.create_logger("Host", "host.log")
        client.log = logger
        host_client.log = logger
    else:
        logger = logging_ex.create_logger("Host")
        client.log = logger
        host_client.log = logger

    client.log_length = config["debug"]["console"]["length"]
    client.log_content = config["debug"]["console"]["content"]

    client.recv_data_log = open("host.recv_data", 'wb')
    client.send_data_log = open("host.send_data", 'wb')


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
