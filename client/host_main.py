# run this file to start your host client
import threading

import client


def main(open_port: int):
    client.init_host()

    host = client.HostClient(client.server_addr[0], open_port)

    functions = [host.send_data, host.get_data, host.virtual_client_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    mc_open_port = int(input("Mc local port: "))
    main(mc_open_port)
