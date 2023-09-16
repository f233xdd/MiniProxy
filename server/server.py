# For the server
import queue
import socket
import sys
import threading
import logging

import queue_ex

#  log config
file_log: bool = True
debug: bool = True
log_length: bool = True
log_context: bool = False

_format_msg = "[%(levelname)s] [%(asctime)s] [%(ip)s] [%(funcName)s] %(message)s"
_format_time = "%H:%M:%S"
_formatter = logging.Formatter(_format_msg, _format_time)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
_console_handler.setLevel(logging.DEBUG)

_log = logging.getLogger("ServerLog")

if debug:
    _log.setLevel(logging.DEBUG)
else:
    _log.setLevel(logging.INFO)
_log.addHandler(_console_handler)

if file_log:
    _file_handler = logging.FileHandler("ServerLog.log", mode='a', encoding='utf-8')
    _file_handler.setFormatter(_formatter)
    _file_handler.setLevel(logging.DEBUG)
    _log.addHandler(_file_handler)

    with open("ServerLog.log", mode='a', encoding='utf_8') as log_file:
        log_file.write("===================================LOG START===================================\n")

#  main context
MAX_LENGTH: int | None = None


class ClientOffLineError(Exception):
    pass


class Server(object):
    _data_queue = queue_ex.DoubleQueue()

    def __init__(self, host: str, port: int):

        self._ip = {'ip': f"{host}:{port}"}
        self._port = port  # work as a port and a queue flag

        self._data_queue.add_flag(port)

        self._get_data_alive = None

        self._client: socket.socket | None = None
        self.client_addr: str | None = None

        # initialize server socket
        self._server_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_port.bind((host, port))
        self._server_port.listen(1)

    def __link_to_client(self):
        """connect to the client"""
        while True:
            client, addr = self._server_port.accept()
            addr = f"{addr[0]}:{addr[1]}"

            _log.info(f"Accept client. Address: {addr}", extra=self._ip)
            try:
                client.send(f"Welcome to the server!\nYour address: {addr}\n".encode('utf_8'))
                break

            except ConnectionResetError:
                _log.warning("[ConnectionResetError] Connection break.", extra=self._ip)

        self._client = client
        self.client_addr = addr
        _log.debug("Gets client", extra=self._ip)

    def __get_data(self):
        """get data from the client and post it into the double queue"""
        self._get_data_alive = True
        _log.info("Get function start.", extra=self._ip)

        try:
            while True:
                data = self._client.recv(MAX_LENGTH)

                if data:
                    msg = ""
                    if log_length:
                        msg = "".join([msg, f"[{len(data)}]"])
                    if log_context:
                        if msg:
                            msg = "".join([msg, ' ', str(data)])
                        else:
                            msg = data

                    if msg:
                        _log.debug(msg, extra=self._ip)

                    self._data_queue.put(data, self._port, exchange=True)

        except ConnectionError as e:
            if e is ConnectionResetError:
                e = "[ConnectionResetError]"
            elif e is ConnectionAbortedError:
                e = "[ConnectionAbortedError]"
            else:
                e = "[ConnectionRefusedError]"

            _log.warning(f"[{e}] Cancelled ip:{self.client_addr}.", extra=self._ip)
            self._get_data_alive = False

    def __send_data(self):
        """get data from the double queue and send it to the client"""
        _log.info("Send function start.", extra=self._ip)

        try:
            while True:
                try:
                    data = self._data_queue.get(self._port, timeout=2)
                except queue.Empty:
                    if self._get_data_alive is False:
                        _log.warning("[TimeoutError] func is down", extra=self._ip)
                        break
                    else:
                        continue

                self._client.sendall(data)

                if data:
                    msg = ""
                    if log_length:
                        msg = "".join([msg, f"[{len(data)}]"])
                    if log_context:
                        if msg:
                            msg = "".join([msg, ' ', str(data)])
                        else:
                            msg = data

                    if msg:
                        _log.debug(msg, extra=self._ip)

        except BrokenPipeError:
            _log.warning(f"[BrokenPipeError] Cancelled ip:{self.client_addr}.", extra=self._ip)

        except ConnectionError as e:
            if e is ConnectionResetError:
                e = "[ConnectionResetError]"
            elif e is ConnectionAbortedError:
                e = "[ConnectionAbortedError]"
            else:
                e = "[ConnectionRefusedError]"

            _log.warning(f"[{e}] Cancelled ip:{self.client_addr}.", extra=self._ip)

    def start(self):
        while True:
            self.__link_to_client()

            threads = [threading.Thread(target=func) for func in [self.__get_data, self.__send_data]]
            _log.info("Threads start", extra=self._ip)

            for thd in threads:
                thd.start()

            for thd in threads:
                thd.join()

            _log.info("Threads are down", extra=self._ip)
