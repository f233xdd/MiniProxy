# run this file to start your host client
import threading
import time

import client


def start(server_addr: tuple[str, int] | None = None,
          open_port: int | None = None,
          crypt: bool | None = None,
          public=None,
          daemon=False):
    addr, port, is_crypt = client.get_attrs("host")

    if server_addr is not None:
        addr = server_addr

    if open_port is not None:
        port = open_port

    if crypt is not None:
        is_crypt = crypt

    if public:
        log = client.get_log("host", public)
    else:
        log = client.get_log("host")

    log.info(f"is_crypt: {is_crypt}")

    host = client.HostClient(addr, port, is_crypt, log)

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
