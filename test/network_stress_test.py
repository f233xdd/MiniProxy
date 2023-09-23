"""this script provides a method of checking the network between you and your friend"""
import socket
import json
import time

#  64 bytes in total
data: bytes = (
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x20\x21\x22\x23\x24\x25\x26"
    b"\x27\x28\x29\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x50\x51\x52"
    b"\x53\x54\x55\x56\x57\x58\x59\x60\x61\x62\x63"
)

config = json.load(open("../client/config.json"))["stress_test"]
MAX_LENGTH: int = config["data_max_length"]
ip: str = config["server_address"]["internet_ip"]
port: int = config["server_address"]["port"]
mode: str = config["mode"]


def check(recv_data: bytes, bag: bytes) -> float:
    return len(recv_data) / len(bag) * 100


def wait(sign: bytes):
    while True:
        recv_data = client.recv(MAX_LENGTH)
        if recv_data != sign:
            continue
        else:
            break


def send():
    bag: bytes = data * int(MAX_LENGTH / 64)
    client.sendall(MAX_LENGTH.to_bytes(8))
    wait(b'GOT')

    for i in range(20):
        client.sendall(bag + f"{time.time()}".encode("utf_8"))
        print(f"send data[{i}]")
        wait(b'GOT')

    client.send(b"END")
    print("\nDone")


def recv():
    global MAX_LENGTH

    MAX_LENGTH = int.from_bytes(client.recv(1024))
    bag: bytes = data * int(MAX_LENGTH / 64)
    client.send(b"GOT")

    i = 0
    while True:
        recv_data = client.recv(MAX_LENGTH + 18)
        recv_time = time.time()

        if recv_data != b"END":
            offset = check(recv_data[:MAX_LENGTH], bag)
            send_time = float(recv_data[MAX_LENGTH:].decode("utf_8"))
            delay = recv_time - send_time

            print(f"recv data[{i}] | offset: {offset}% | delay: {delay}ms")
        else:

            print("\nDone")
            break

        client.send(b'GOT')
        i += 1


if mode == "s":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(1)
    client, __ = server.accept()

    send()
elif mode == "r":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    recv()
else:
    raise ValueError
