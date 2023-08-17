import socket

data: bytes = (
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x20\x21\x22\x23\x24\x25\x26"
    b"\x27\x28\x29\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x50\x51\x52"
    b"\x53\x54\x55\x56\x57\x58\x59\x60\x61\x62\x63"
)

MAX_LENGTH = None
addr = (socket.gethostname(), 25566)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(addr)


def check(recv_data: bytes, bag: bytes) -> float:
    return len(recv_data) / len(bag) * 100


def wait(sign: bytes):
    while True:
        recv_data = client.recv(MAX_LENGTH)
        if recv_data != sign:
            continue
        else:
            break


def recv():
    global MAX_LENGTH

    d = client.recv(1024)
    MAX_LENGTH = int.from_bytes(d)
    bag: bytes = data * int(MAX_LENGTH / 128)
    client.sendall(b"GOT")

    i = 0
    while True:
        recv_data = client.recv(MAX_LENGTH)
        if recv_data != b"END":
            print(f"recv data[{i}] | offset: {check(recv_data, bag)}%")
        else:
            break
        client.sendall(b'GOT')
        i += 1

    for j in range(i):
        client.sendall(bag)
        print(f"send data[{j}]")
        wait(b'GOT')

    client.sendall(b"END")
    print("\nDone")


recv()