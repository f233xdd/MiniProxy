# visitor client
import threading
import json

import visitor
import client

server_addr: tuple[str, int]
virtual_port: int


def init():
    """set up basic config"""
    global server_addr, virtual_port

    file = open("config.json")
    visitor_config = json.load(file)["visitor"]

    client.MAX_LENGTH = visitor_config["data_max_length"]
    addr = visitor_config["server_address"].split(':')
    server_addr = addr[0], int(addr[1])
    virtual_port = visitor_config["virtual_open_port"]
    visitor.debug = visitor_config["debug"]


def main():
    init()

    mc_port = visitor.VisitClient(server_addr, virtual_port)

    functions1 = (mc_port.send_data, mc_port.get_data)
    functions2 = (mc_port.get_local_data, mc_port.send_java_data)

    threads1 = [threading.Thread(target=func) for func in functions1]
    threads2 = [threading.Thread(target=func) for func in functions2]

    for thread in threads1:
        thread.start()

    for thread in threads2:
        thread.start()


if __name__ == "__main__":
    main()
