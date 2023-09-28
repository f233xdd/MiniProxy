import json
import os

from .client import *
from .host_client import *
from .visitor_client import *

from . import (client, host_client, visitor_client)

from .logging_ex import create_logger

server_addr: list[tuple[str, int], tuple[str, int]] = []
virtual_port: int | None = None

__all__ = ["Client", "HostClient", "VisitClient",
           "server_addr", "virtual_port",
           "init_host", "init_visitor"]

basic_path = os.getcwd() + "\\client"
file = open(basic_path + "\\config.json", 'r')
config = json.load(file)
h_config = config["host"]
v_config = config["visitor"]


def init_host():
    """set up host basic config"""
    client.MAX_LENGTH = h_config["data_max_length"]
    addr = h_config["server_address"]
    server_addr.append((addr["internet_ip"], addr["port"]))

    client.log_length = h_config["debug"]["console"]["length"]
    client.log_content = h_config["debug"]["console"]["content"]

    if h_config["debug"]["file_log"]:
        logger = create_logger("Host", basic_path + "\\log\\host.log")
        client.log = logger
        host_client.log = logger
    else:
        logger = create_logger("Host")
        client.log = logger
        host_client.log = logger

    client.recv_data_log = open(basic_path + "\\log\\host.recv_data", 'wb')
    client.send_data_log = open(basic_path + "\\log\\host.send_data", 'wb')


def init_visitor():
    """set up visitor basic config"""
    global virtual_port

    client.MAX_LENGTH = v_config["data_max_length"]
    addr = v_config["server_address"]
    server_addr.append((addr["internet_ip"], addr["port"]))
    virtual_port = v_config["virtual_open_port"]

    client.log_length = v_config["debug"]["console"]["length"]
    client.log_content = v_config["debug"]["console"]["content"]

    if v_config["debug"]["file_log"]:
        logger = create_logger("Visitor", basic_path + "\\log\\visitor.log")
        client.log = logger
        visitor_client.log = logger
    else:
        logger = create_logger("Visitor")
        client.log = logger
        visitor_client.log = logger

    client.recv_data_log = open(basic_path + "\\log\\visitor.recv_data", 'wb')
    client.send_data_log = open(basic_path + "\\log\\visitor.send_data", 'wb')
