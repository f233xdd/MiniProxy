import json
import os
import copy

from .client import Client
from .host_client import HostClient
from .visitor_client import VisitClient

from .tool import get_logger

__all__ = ["Client", "HostClient", "VisitClient",
           "server_addr", "virtual_port", "conf",
           "init_host", "init_visitor"]

server_addr: list[tuple[str, int], tuple[str, int]] = []
virtual_port: int | None = None

local_path = os.getcwd() + "\\client"

if not os.path.exists(local_path + "\\log"):
    os.mkdir(local_path + "\\log")


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
        v = self._conf

        for k in keys:
            v = v[k]

        return copy.deepcopy(v)

    def __repr__(self):
        return f"updated: {self._updated} | {self._conf}"


conf = Config(local_path + "\\config.json")


def init_host():
    """set up host basic config"""
    client.MAX_LENGTH = conf["host", "data_max_length"]
    addr = conf["host", "server_address"]
    server_addr.append((addr["internet_ip"], addr["port"]))

    client.log_length = conf["host", "debug", "console", "length"]
    client.log_content = conf["host", "debug", "console", "content"]

    if conf["host", "debug", "clear_log"]:
        try:
            os.remove(local_path + "\\log\\host.log")
            os.remove(local_path + "\\log\\host.send_data")
            os.remove(local_path + "\\log\\host.recv_data")
        except FileNotFoundError:
            pass

    if conf["host", "debug", "file_log"]:
        logger = get_logger("Host", local_path + "\\log\\host.log")
        client.log = logger
        host_client.log = logger
    else:
        logger = get_logger("Host")
        client.log = logger
        host_client.log = logger

    # client.recv_data_log = open(local_path + "\\log\\host.recv_data", 'wb')
    # client.send_data_log = open(local_path + "\\log\\host.send_data", 'wb')


def init_visitor():
    """set up visitor basic config"""
    global virtual_port

    client.MAX_LENGTH = conf["visitor", "data_max_length"]
    addr = conf["host", "server_address"]
    server_addr.append((addr["internet_ip"], addr["port"]))
    virtual_port = conf["visitor", "virtual_open_port"]

    client.log_length = conf["visitor", "debug", "console", "length"]
    client.log_content = conf["visitor", "debug", "console", "content"]

    if conf["visitor", "debug", "clear_log"]:
        try:
            os.remove(local_path + "\\log\\visitor.log")
            os.remove(local_path + "\\log\\visitor.send_data")
            os.remove(local_path + "\\log\\visitor.recv_data")
        except FileNotFoundError:
            pass

    if conf["visitor", "debug", "file_log"]:
        logger = get_logger("Visitor", local_path + "\\log\\visitor.log")
        client.log = logger
        visitor_client.log = logger
    else:
        logger = get_logger("Visitor")
        client.log = logger
        visitor_client.log = logger

    # client.recv_data_log = open(local_path + "\\log\\visitor.recv_data", 'wb')
    # client.send_data_log = open(local_path + "\\log\\visitor.send_data", 'wb')
