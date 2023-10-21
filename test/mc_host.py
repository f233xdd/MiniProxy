import socket
import threading
import time
import struct

import log

data: bytes = (
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x20\x21\x22\x23\x24\x25\x26"
    b"\x27\x28\x29\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x50\x51\x52"
    b"\x53\x54\x55\x56\x57\x58\x59\x60\x61\x62\x63"
)

MAX_LENGTH = 524288
addr = (socket.gethostname(), 9999)
_log = log.create_logger("MC_host", log_file="mc_host.log")


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
    for i in range(2000):
        client.sendall(bag + struct.pack('d', time.time()))
        time.sleep(0.05)
    client.send(b"END")


def recv():
    try:
        i = 0
        while True:
            recv_data = client.recv(MAX_LENGTH + 8)
            recv_time = time.time()

            if recv_data != b"END":
                offset = check(recv_data[:MAX_LENGTH], bag)
                _log.debug(len(recv_data))
                send_time = struct.unpack('d', recv_data[MAX_LENGTH:])[0]
                delay = round(recv_time - send_time, 3) * 1000

                _log.info(f"recv data[{i}] | offset: {offset}% | delay: {delay}ms")
                i += 1
            else:
                break
    except Exception as e:
        _log.error(len(recv_data))
        _log.error(e)


def init():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(addr)
    server.listen(1)
    _client, __ = server.accept()

    _bag: bytes = data * int(MAX_LENGTH / 64)
    _client.sendall(struct.pack('i', MAX_LENGTH))

    return _client, _bag


def start():
    thds = [threading.Thread(target=send), threading.Thread(target=recv)]

    for thd in thds:
        thd.start()

    for thd in thds:
        thd.join()

    print("Done")


if __name__ == '__main__':
    client, bag = init()
    wait(b'GOT')

    start()