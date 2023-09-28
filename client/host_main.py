# run this file to start your host client
import threading

import client


def main():
    client.init_host()

    mc_open_port = int(input("Mc local port: "))
    host = client.HostClient(client.server_addr[0], mc_open_port)

    functions = [host.send_data, host.get_data, host.virtual_client_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
