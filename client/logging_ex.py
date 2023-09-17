import logging
import sys

from typing import Mapping


def create_logger(name, log_file: str = ""):
    _format_msg = "[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s"
    _format_time = "%H:%M:%S"

    _formatter = logging.Formatter(_format_msg, _format_time)

    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setFormatter(_formatter)
    _console_handler.setLevel(logging.INFO)

    _log = logging.getLogger(name)
    _log.setLevel(logging.DEBUG)
    _log.addHandler(_console_handler)

    if log_file:
        _file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        _file_handler.setFormatter(_formatter)
        _file_handler.setLevel(logging.DEBUG)

        with open(log_file, mode='a+', encoding='utf_8') as log_file:
            log_file.write("===================================LOG START===================================\n")
        _log.addHandler(_file_handler)

    return _log


def log_debug_msg(data, logger: logging.Logger, en_context: bool, en_length: bool,
                  add_msg: str | None = None, extra: Mapping = None):
    if data:
        msg = ""
        if en_length:
            msg = "".join([msg, f"[{len(data)}]"])
        if en_context:
            if msg:
                msg = "".join([msg, ' ', str(data)])
            else:
                msg = data
        if msg:
            if add_msg:
                logger.debug(f"{add_msg} {msg}", extra=extra)
            else:
                logger.debug(msg, extra=extra)