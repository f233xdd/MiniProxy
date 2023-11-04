# run this file to start your visitor client
import threading
import time

import client


def start(server_addr: tuple[str, int] | None = None,
          virtual_port: int | None = None,
          crypt: bool | None = None,
          public=None,
          daemon=False):
    addr, port, is_crypt = client.get_attrs("guest")

    if server_addr:
        addr = server_addr

    if virtual_port:
        port = virtual_port

    if crypt:
        is_crypt = crypt

    print("is_crypt: ", is_crypt)

    if public:
        log = client.get_log("guest", public)
    else:
        log = client.get_log("guest")

    guest = client.GuestClient(addr, port, is_crypt, log)

    functions = [guest.send_server_data, guest.get_server_data, guest.local_server_main]

    if __name__ == "__main__":
        daemon = True

    threads = [threading.Thread(target=func, daemon=daemon) for func in functions]

    for thread in threads:
        thread.start()


def main(server_addr: tuple[str, int] | None = None,
         virtual_port: int | None = None,
         public=None):
    start(server_addr, virtual_port, public)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Canceled by [Ctrl-C]")


if __name__ == "__main__":
    main()
