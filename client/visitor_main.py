# run this file to start your visitor client
import sys
import threading

import client


def main(server_addr: tuple[str, int] | None = None,
         virtual_port: int | None = None,
         public=None):
    client._init_visitor_execute()

    if server_addr:
        addr = server_addr
    else:
        addr = client.server_addr["visitor"]

    if virtual_port:
        port = virtual_port
    else:
        port = client.virtual_port

    if public:
        client._init_visitor_log(public)
    else:
        client._init_visitor_log(sys.stderr)

    try:
        visitor = client.VisitClient(addr, port)
    except ConnectionRefusedError as e:
        client.client.log.error(e)
        sys.exit(-1)

    functions = [visitor.send_server_data, visitor.get_server_data, visitor.local_server_main]

    threads = [threading.Thread(target=func) for func in functions]

    for thread in threads:
        thread.start()


if __name__ == "__main__":
    main()
