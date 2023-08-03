import socket

from client import MAX_LENGTH


def listener():
    reflect_port = 2000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), reflect_port))

    print("Listener running!\n")
    while True:
        data = sock.recv(MAX_LENGTH)
        print(f"[In] {data.decode('utf_8')}")


if __name__ == '__main__':
    listener()
