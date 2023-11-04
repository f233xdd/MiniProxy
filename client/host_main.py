# run this file to start your host client
import threading
import time

import client


def start(
        server_addr: tuple[str, int] | None = None,
        open_port: int | None = None,
        public=None,
        daemon=False):
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
        log = client._init_host_log(public)
    else:
        log = client._init_host_log()

    host = client.HostClient(addr, port, False, log)

    functions = [host.send_server_data, host.get_server_data, host.local_client_main]

    if __name__ == "__main__":
        daemon = True

    threads = [threading.Thread(target=func, daemon=daemon) for func in functions]

    for thread in threads:
        thread.start()


def main(
        server_addr: tuple[str, int] | None = None,
        open_port: int | None = None,
        public=None):
    start(server_addr, open_port, public)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Canceled by [Ctrl-C]")


if __name__ == "__main__":
    mc_open_port = int(input("Mc local port: "))

    main(open_port=mc_open_port)
