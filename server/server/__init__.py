import json
import logging
import os

from .server import Server
from .tool import get_logger

__all__ = ["Server", "get_attrs", "get_log", "log"]

local_path = os.getcwd() + "/server"

json_file = open("server/config.json")
config = json.load(json_file)


# init execution
def get_attrs() -> tuple[str, list[int, int], int]:
    MAX_LENGTH = config["data_max_length"]
    local_ip = config["local_address"]["private_ip"]
    local_ports = config["local_address"]["ports"]
    return local_ip, local_ports, MAX_LENGTH


# init log
def get_log() -> logging.Logger:
    if not os.path.exists(local_path + "/log"):
        os.mkdir(local_path + "/log")
    else:
        if config["debug"]["clear_log"]:
            try:
                os.remove(local_path + "/log/server.log")
            except FileNotFoundError:
                pass
            except PermissionError as e:
                # there might be other process using the log file
                # usually caused for incompletely exiting python
                print(f"[WARNING] there's an error that might cause file log not working:\n{e}")
                print(
                    "[INFO] Check your explorer to find if there's another python process running and interrupt it"
                )

    if config["debug"]["file_log"]:
        log = get_logger("Server", local_path + "/log/server.log")
    else:
        log = get_logger("Sever")

    server.log_length = config["debug"]["console"]["length"]
    server.log_content = config["debug"]["console"]["content"]

    return log
