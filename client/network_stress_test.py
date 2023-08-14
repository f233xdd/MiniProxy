"""this script provides a method of checking the network between you and your friend"""
import socket
import json

#  128 bytes in total
data: bytes = (
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x20\x21\x22\x23\x24\x25\x26"
    b"\x27\x28\x29\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x50\x51\x52"
    b"\x53\x54\x55\x56\x57\x58\x59\x60\x61\x62\x63"
)

config = json.load(open("config.json"))["stress_test"]
MAX_LENGTH: int = config["data_max_length"]
ip: str = config["server_address"]["internet_ip"]
port: int = config["server_address"]["port"]
mode: str = config["mode"]


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port))
print(client.recv(1024).decode("utf_8"))


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
    bag: bytes = data * int(MAX_LENGTH / 128)
    client.sendall(f"{MAX_LENGTH}".encode("utf_8"))
    wait(b'\x00\x00\x00')

    for i in range(10):
        client.sendall(bag)
        print(f"send data[{i}]")
        wait(b'\x00\x00\x00')


def recv():
    global MAX_LENGTH

    MAX_LENGTH = int(client.recv(1024).decode("utf_8"))
    bag: bytes = data * int(MAX_LENGTH / 128)
    client.sendall(b"\x00\x00\x00")

    for i in range(10):
        recv_data = client.recv(MAX_LENGTH)
        print(f"recv data[{i}] offset: {check(recv_data, bag)}%")
        client.sendall(b'\x00\x00\x00')


if mode == "send":
    send()
elif mode == "recv":
    recv()
else:
    raise ValueError

"""
def test(recv_data: bytes) -> int:
    check_len = 0
    offset = 0

    while check_len != MAX_LENGTH:
        split = recv_data[check_len:check_len + 128]
        if split == data:
            check_len += 128
        else:
            if len(split) == len(data):
                for s1, s2 in zip(data, split):
                    if s1 != s2:
                        pass  # TODO: how?
            else:
                k = 0
                v = 0
                while k != 128:
                    if split[k] != data[v]:
                        k += 1
                        offset += 1
                        continue
                    else:
                        k += 1
                        v += 1

    return offset
"""
