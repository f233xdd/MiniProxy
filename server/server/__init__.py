import json
import os
import shutil

from .server import Server
from .logging_ex import create_logger

__all__ = ["Server", "local_addr"]

local_path = os.getcwd() + "\\server"
local_addr: tuple[str, list[int, int]] | None = None

json_file = open("server/config.json")
config = json.load(json_file)

if config["debug"]["clear_log"]:
    shutil.rmtree(local_path + "\\log")

if not os.path.exists(local_path + "\\log"):
    os.mkdir(local_path + "\\log")


server.MAX_LENGTH = config["data_max_length"]
local_addr = config["local_address"]["private_ip"], config["local_address"]["ports"]
print(local_addr)

if config["debug"]["file_log"]:
    server.log = create_logger("Server", local_path + "\\log\\server.log")
else:
    server.log = create_logger("Sever")

server.log_length = config["debug"]["console"]["length"]
server.log_content = config["debug"]["console"]["content"]