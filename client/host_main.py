# host client
import threading
import json

import host
import client

server_addr: tuple[str, int]


def init():
    """set up basic config"""
    global server_addr

    file = open("config.json")
    host_config = json.load(file)["host"]

    client.MAX_LENGTH = host_config["data_max_length"]
    addr = host_config["server_address"].split(':')
    server_addr = addr[0], int(addr[1])
    host.debug = host_config["debug"]


def main():
    init()

    open_port = int(input("Mc local port: "))
    mc_port = host.HostClient(server_addr, open_port)

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
