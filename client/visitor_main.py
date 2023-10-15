# run this file to start your visitor client
import sys
import threading

import client


def main(virtual_port: int | None = None, public=None):
    # TODO: Manual filling
    if virtual_port:
        port = virtual_port
    else:
        port = client.virtual_port

    print("host main", client.server_addr)
    visitor = client.VisitClient(client.server_addr[1], port)

    functions = [visitor.send_data, visitor.get_data, visitor.virtual_server_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    client.init_visitor(sys.stderr)
    main()
