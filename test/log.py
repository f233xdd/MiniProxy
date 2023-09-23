import logging
import sys


def create_logger(name, log_file: str = ""):
    format_msg = "[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s"
    format_time = "%H:%M:%S"

    formatter = logging.Formatter(format_msg, format_time)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(console_handler)

    if log_file:
        _file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        _file_handler.setFormatter(formatter)
        _file_handler.setLevel(logging.DEBUG)

        with open(log_file, mode='a+', encoding='utf_8') as log_file:
            log_file.write("===================================LOG START===================================\n")
        log.addHandler(_file_handler)

    return log