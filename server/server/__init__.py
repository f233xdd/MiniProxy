import json
import os
import shutil

from .server import Server
from .tool import get_logger

__all__ = ["Server", "local_addr"]

local_path = os.getcwd() + "/server"
local_addr: tuple[str, list[int, int]] | None = None

json_file = open("server/config.json")
config = json.load(json_file)

if os.path.exists(local_path + "/log"):
    if config["debug"]["clear_log"]:
        shutil.rmtree(local_path + "/log")
else:
    os.mkdir(local_path + "/log")

server.MAX_LENGTH = config["data_max_length"]
local_addr = config["local_address"]["private_ip"], config["local_address"]["ports"]

if config["debug"]["file_log"]:
    server.log = get_logger("Server", local_path + "/log/server.log")
else:
    server.log = get_logger("Sever")

server.log_length = config["debug"]["console"]["length"]
server.log_content = config["debug"]["console"]["content"]