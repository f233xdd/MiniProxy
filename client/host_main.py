# run this file to start your host client
import sys
import threading
import time

import client


def main(
        server_addr: tuple[str, int] | None = None,
        open_port: int | None = None,
        public=None):
    print("main: ", public)
    client._init_host_execute()
    if server_addr:
        addr = server_addr
    else:
        addr = client.server_addr["host"]

    if open_port:
        port = open_port
    else:
        port = client.open_port

    if public:
        client._init_host_log(public)
    else:
        client._init_host_log(sys.stderr)
    #
    # host = client.HostClient(addr, port)
    #
    # functions = [host.send_data, host.get_data, host.virtual_client_main]
    #
    # threads = [threading.Thread(target=func) for func in functions]
    #
    # for thread in threads:
    #     thread.start()
    for i in range(5):
        client.client.log.info(f"TEST[{i}]")
        time.sleep(1)

    print("Done!")


if __name__ == "__main__":
    mc_open_port = int(input("Mc local port: "))

    main(open_port=mc_open_port)
