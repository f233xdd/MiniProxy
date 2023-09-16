import logging
import sys


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
