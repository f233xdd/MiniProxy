# run this file to start visitor client
import threading

import client


def main():
    client.init_visitor()

    visitor = client.VisitClient(client.server_addr[0], client.virtual_port)

    functions = [visitor.send_data, visitor.get_data, visitor.virtual_server_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
