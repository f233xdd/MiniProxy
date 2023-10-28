import json
import os
import copy

from .client import Client
from .host_client import HostClient
from .guest_client import GuestClient

from .tool import get_logger, crypto_available

__all__ = ["Client", "HostClient", "GuestClient",
           "_init_host_execute", "_init_host_log",
           "_init_guest_execute", "_init_guest_log",
           "server_addr", "open_port", "virtual_port",
           "conf", "crypto_available"]

HOST = "host"
GUEST = "guest"

server_addr: dict[str: tuple[str, int], str: tuple[str, int]] = {"host": ('', 0), "guest": ('', 0)}
open_port: int | None = None
virtual_port: int | None = None

local_path = os.getcwd() + "/client"

if not os.path.exists(local_path + "/log"):
    os.mkdir(local_path + "/log")


class Config:

    def __init__(self, cfile: str):
        self._f_conf = open(cfile, "r+", encoding='utf_8')
        self._conf: dict = json.load(self._f_conf)

        self._updated: bool = True

    def update(self, value, keys: list):
        slc = self._conf
        end = keys.pop(-1)

        for k in keys:
            slc = slc[k]

        slc[end] = value

        self._updated = False

    def save(self):
        self._f_conf.seek(0)
        self._f_conf.truncate()
        self._f_conf.write(json.dumps(self._conf, sort_keys=True, indent=2))
        self._f_conf.flush()
        self._updated = True

    def close(self):
        self._f_conf.close()

    def __getitem__(self, keys):
        if isinstance(keys, str):
            keys = (keys,)

        v = self._conf

        for k in keys:
            v = v[k]

        return copy.deepcopy(v)

    def __repr__(self):
        return f"updated: {self._updated} | {self._conf}"


class ClientConfig(Config):

    def get_func_args(self, func: str) -> tuple[tuple[str, int], int]:
        if func == HOST:
            return ((self[HOST, "server_address", "internet_ip"], self[HOST, "server_address", "port"]),
                    self[HOST, "open_port"])
        elif func == GUEST:
            return ((self[GUEST, "server_address", "internet_ip"], self[GUEST, "server_address", "port"]),
                    self[GUEST, "virtual_open_port"])

    def __getitem__(self, keys):
        if keys == "crypto" and not crypto_available:
            return False
        else:
            return super().__getitem__(keys)


conf = ClientConfig(local_path + "/config.json")


def _init_host_execute():
    global open_port

    client.MAX_LENGTH = conf[HOST, "data_max_length"]

    addr = conf[HOST, "server_address"]
    server_addr[HOST] = (addr["internet_ip"], addr["port"])

    open_port = conf[HOST, "open_port"]


def _init_host_log(stream):
    """set up host basic config"""

    client.log_length = conf[HOST, "debug", "console", "length"]
    client.log_content = conf[HOST, "debug", "console", "content"]

    if conf[HOST, "debug", "clear_log"]:
        try:
            os.remove(local_path + "/log/host.log")
            os.remove(local_path + "/log/host.send_data")
            os.remove(local_path + "/log/host.recv_data")
        except FileNotFoundError:
            pass

    if conf[HOST, "debug", "file_log"]:
        logger = get_logger(HOST, local_path + "/log/host.log", stream=stream)
        client.log = logger
        host_client.log = logger
    else:
        logger = get_logger(HOST, stream=stream)
        client.log = logger
        host_client.log = logger

    # client.recv_data_log = open(local_path + "/log/host.recv_data", 'wb')
    # client.send_data_log = open(local_path + "/log/host.send_data", 'wb')


def _init_guest_execute():
    global virtual_port

    client.MAX_LENGTH = conf[GUEST, "data_max_length"]

    addr = conf[GUEST, "server_address"]
    server_addr[GUEST] = (addr["internet_ip"], addr["port"])

    virtual_port = conf[GUEST, "virtual_open_port"]


def _init_guest_log(stream):
    """set up guest basic config"""

    client.log_length = conf[GUEST, "debug", "console", "length"]
    client.log_content = conf[GUEST, "debug", "console", "content"]

    if conf[GUEST, "debug", "clear_log"]:
        try:
            os.remove(local_path + "/log/guest.log")
            os.remove(local_path + "/log/guest.send_data")
            os.remove(local_path + "/log/guest.recv_data")
        except FileNotFoundError:
            pass

    if conf[GUEST, "debug", "file_log"]:
        logger = get_logger(GUEST, local_path + "/log/guest.log", stream=stream)
        client.log = logger
        guest_client.log = logger
    else:
        logger = get_logger(GUEST, stream=stream)
        client.log = logger
        guest_client.log = logger

    # client.recv_data_log = open(local_path + "/log/guest.recv_data", 'wb')
    # client.send_data_log = open(local_path + "/log/guest.send_data", 'wb')
