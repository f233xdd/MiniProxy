import json
import logging
import os
import copy
import sys
import typing

from .client import Client
from .host_client import HostClient
from .guest_client import GuestClient

from .tool import get_logger, crypt_available

__all__ = ["Client", "HostClient", "GuestClient",
           "get_attrs", "get_log",
           "conf", "crypt_available"]

HOST = "host"
GUEST = "guest"

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

    def get_func_args(self, func: str) -> tuple[tuple[str, int], int, bool]:
        if func == HOST:
            return ((self[HOST, "server_address", "internet_ip"], self[HOST, "server_address", "port"]),
                    self[HOST, "open_port"], self["crypt"])
        elif func == GUEST:
            return ((self[GUEST, "server_address", "internet_ip"], self[GUEST, "server_address", "port"]),
                    self[GUEST, "virtual_open_port"], self["crypt"])

    def __getitem__(self, keys):
        if keys == "crypt" and not crypt_available:
            return False
        else:
            return super().__getitem__(keys)


conf = ClientConfig(local_path + "/config.json")


def get_attrs(owner: typing.Literal["host", "guest"]) -> tuple[tuple[str, int], int, bool]:
    client.MAX_LENGTH = conf[owner, "data_max_length"]

    addr = conf[owner, "server_address"]

    server_addr = (addr["internet_ip"], addr["port"])
    is_crypt = conf["crypt"]

    if owner == HOST:
        open_port = conf[owner, "open_port"]
        return server_addr, open_port, is_crypt

    elif owner == GUEST:
        virtual_port = conf[owner, "virtual_open_port"]
        return server_addr, virtual_port, is_crypt
    else:
        raise ValueError(owner)


def get_log(owner: typing.Literal["host", "guest"], stream=sys.stdout) -> logging.Logger:
    """set up host basic config"""

    client.log_length = conf[owner, "debug", "console", "length"]
    client.log_content = conf[owner, "debug", "console", "content"]

    if conf[owner, "debug", "clear_log"]:
        try:
            os.remove(local_path + f"/log/{owner}.log")
            os.remove(local_path + f"/log/{owner}.send_data")
            os.remove(local_path + f"/log/{owner}.recv_data")
        except FileNotFoundError:
            pass

    # client.recv_data_log = open(local_path + f"/log/{owner}.recv_data", 'wb')
    # client.send_data_log = open(local_path + f"/log/{owner}.send_data", 'wb')

    if conf[owner, "debug", "file_log"]:
        return get_logger(owner, local_path + f"/log/{owner}.log", stream=stream)
    else:
        return get_logger(owner, stream=stream)
