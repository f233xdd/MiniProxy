# run this file to start visitor client
import threading
import json

import visitor_client
import client

server_addr: tuple[str, int] = ('', -1)
virtual_port: int = -1


def init():
    """set up basic config"""
    global server_addr, virtual_port

    file = open("config.json")
    visitor_config = json.load(file)["visitor"]

    client.MAX_LENGTH = visitor_config["data_max_length"]
    addr = visitor_config["server_address"]
    server_addr = addr["internet_ip"], addr["port"]
    virtual_port = visitor_config["virtual_open_port"]
    client.debug = visitor_config["debug"]


def main():
    init()

    visitor = visitor_client.VisitClient(server_addr, virtual_port)

    functions = [visitor.send_data, visitor.get_data, visitor.virtual_server_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
