import json
import os

from .server import Server
from .tool import get_logger

__all__ = ["Server", "local_ip", "local_ports", "log"]

local_path = os.getcwd() + "/server"

json_file = open("server/config.json")
config = json.load(json_file)

# init execution
server.MAX_LENGTH = config["data_max_length"]
local_ip = config["local_address"]["private_ip"]
local_ports = config["local_address"]["ports"]

# init log
if not os.path.exists(local_path + "/log"):
    os.mkdir(local_path + "/log")
else:
    if config["debug"]["clear_log"]:
        try:
            os.remove(local_path + "/log/server.log")
        except (FileNotFoundError, PermissionError):
            pass

if config["debug"]["file_log"]:
    log = get_logger("Server", local_path + "/log/server.log")
else:
    log = get_logger("Sever")

server.log_length = config["debug"]["console"]["length"]
server.log_content = config["debug"]["console"]["content"]
