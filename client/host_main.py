# run this file to start your host client
import sys
import threading

import client


def main(open_port: int | None = None, public=None):
    # TODO: Manual filling
    if open_port:
        port = open_port
    else:
        port = client.open_port

    print("host main", client.server_addr)
    host = client.HostClient(client.server_addr[0], port)

    functions = [host.send_data, host.get_data, host.virtual_client_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    mc_open_port = int(input("Mc local port: "))
    client.init_host(sys.stderr)

    main(mc_open_port)
