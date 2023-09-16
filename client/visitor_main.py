# run this file to start visitor client
import threading
import json

import visitor_client
import client

import logging_ex

server_addr: tuple[str, int] = ('', -1)
virtual_port: int = -1


def init():
    """set up basic config"""
    global server_addr, virtual_port

    file = open("config.json")
    config = json.load(file)["visitor"]

    client.MAX_LENGTH = config["data_max_length"]
    addr = config["server_address"]
    server_addr = addr["internet_ip"], addr["port"]
    virtual_port = config["virtual_open_port"]

    if config["file_log"]:
        logger = logging_ex.create_logger("Visitor", "visitor.log")
        client.log = logger
        visitor_client.log = logger
    else:
        logger = logging_ex.create_logger("Visitor")
        client.log = logger
        visitor_client.log = logger

    client.log_length = config["console"]["length"]
    client.log_context = config["console"]["context"]


def main():
    init()

    visitor = visitor_client.VisitClient(server_addr, virtual_port)

    functions = [visitor.send_data, visitor.get_data, visitor.virtual_server_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
