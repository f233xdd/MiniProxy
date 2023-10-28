# run this file to start your host client
import sys
import threading

import client


def start(
        server_addr: tuple[str, int] | None = None,
        open_port: int | None = None,
        public=None):
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

    try:
        host = client.HostClient(addr, port)
    except ConnectionRefusedError as e:
        client.client.log.error(e)
        sys.exit(-1)

    functions = [host.send_server_data, host.get_server_data, host.local_client_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


def main(
        server_addr: tuple[str, int] | None = None,
        open_port: int | None = None,
        public=None):
    start(server_addr, open_port, public)


if __name__ == "__main__":
    mc_open_port = int(input("Mc local port: "))

    main(open_port=mc_open_port)
