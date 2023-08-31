import socket
import threading
import time

data: bytes = (
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x20\x21\x22\x23\x24\x25\x26"
    b"\x27\x28\x29\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x50\x51\x52"
    b"\x53\x54\x55\x56\x57\x58\x59\x60\x61\x62\x63"
)

MAX_LENGTH = None
addr = (socket.gethostname(), 25566)


def check(recv_data: bytes, complete: bytes) -> float:
    return len(recv_data) / len(complete) * 100


def wait(sign: bytes):
    while True:
        recv_data = client.recv(MAX_LENGTH)
        if recv_data != sign:
            continue
        else:
            break


def send():
    for i in range(30):
        client.sendall(bag + f"{time.time()}".encode("utf_8"))
        print(f"send data[{i}]")
        wait(b'GOT')

    client.send(b"END")


def recv():
    i = 0
    while True:
        recv_data = client.recv(MAX_LENGTH + 18)
        recv_time = time.time()

        if recv_data != b"END":
            offset = check(recv_data[:MAX_LENGTH], bag)
            send_time = float(recv_data[MAX_LENGTH:].decode("utf_8"))
            delay = round(recv_time - send_time, 3) * 1000

            print(f"recv data[{i}] | offset: {offset}% | delay: {delay}ms")
        else:
            break

        client.send(b'GOT')
        i += 1


def init():
    _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _client.connect(addr)

    d = _client.recv(1024)
    _MAX_LENGTH = int.from_bytes(d)
    _bag: bytes = data * int(_MAX_LENGTH / 64)

    return _client, _bag, _MAX_LENGTH


def start():
    recv()
    send()


if __name__ == '__main__':
    client, bag, MAX_LENGTH = init()
    client.send(b"GOT")

    start()