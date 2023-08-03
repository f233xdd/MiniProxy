import socket

open_ports = 25565
MAX_LENGTH = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((socket.gethostname(), open_ports))
print(f"Open port at {open_ports}.")

server.listen(3)

while True:
    client, __ = server.accept()
    print("Accept client.")

    for i in range(100):
        client.sendall(f"Data[{i}] from host.".encode('utf_8'))
        print(f"Send Data[{i}]")

        data = client.recv(MAX_LENGTH)
        print(data.decode('utf_8'))

    client.close()
