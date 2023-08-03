import socket
import time

server_port = 2000
MAX_LENGTH = 4096

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), server_port))
print("Connection established.")

i = 0
while True:
    data = client.recv(MAX_LENGTH)
    print(data.decode('utf_8'))

    client.sendall(f"Data[{i}] from  visitor.".encode('utf_8'))
    print(f"Send data[{i}]")
    time.sleep(1)
    i += 1