# For the server
import queue
import socket
import sys
import threading
import time
import logging

import queue_ex

#  log config
file_log = True

_format_msg = "[%(levelname)s] [%(asctime)s] [%(ip)s] [%(funcName)s] %(message)s"
_format_time = "%H:%M:%S"

_formatter = logging.Formatter(_format_msg, _format_time)

_file_handler = logging.FileHandler("ServerLog.log", mode='a', encoding='utf-8')
_file_handler.setFormatter(_formatter)
_file_handler.setLevel(logging.DEBUG)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
_console_handler.setLevel(logging.DEBUG)

_log = logging.getLogger("ServerLog")
_log.setLevel(logging.DEBUG)
_log.addHandler(_console_handler)
if file_log:
    _log.addHandler(_file_handler)

    with open("ServerLog.log", mode='a', encoding='utf_8') as log_file:
        log_file.write("===================================LOG START===================================\n")

#  main context
MAX_LENGTH: int | None = None


class ClientOffLineError(Exception):
    pass


class Server(object):
    _queue = queue_ex.DoubleQueue()

    def __init__(self, host: str, port: int):
        # TODO: In the future we'll add the function about the arg 'mode'

        self._ip = {'ip': f"{host}:{port}"}
        self._port = port  # work as a port and a queue flag
        self._cache: bytes | None = None  # store data which is not sent yet

        self._queue.add_flag(port)

        self._data_queue = queue.Queue()

        self._get_func_alive = False
        self._send_func_alive = False

        self._client: socket.socket | None = None
        self._client_addr: tuple | None = None
        self._to_client: socket.socket | None = None

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
                client.sendall(f"Welcome to the server!\nYour address: {addr}\n".encode('utf_8'))
                break

            except ConnectionResetError:
                _log.warning("[ConnectionResetError] Connection break.", extra=self._ip)

        self._client: socket.socket = client
        self._client_addr: str = addr

        self._queue.put(self._client, self._port)

    def __get_to_client(self):
        while True:
            try:
                self._to_client = self._queue.get(self._port, timeout=3)
                break

            except (TimeoutError, queue.Empty):  # avoid a client is not alive, to_client has not linked
                # and it is stuck forever
                if not self._get_func_alive:  # when get function is not running, which means the client is not alive
                    raise ClientOffLineError  # break the loop to stop sticking the whole thread

    def __get_data(self):
        """get data from the client and post it into a queue"""
        self._get_func_alive = True
        _log.info("Get function start.", extra=self._ip)

        try:
            while True:
                data = self._client.recv(MAX_LENGTH)
                self._data_queue.put(data)

        except (ConnectionResetError, TimeoutError) as error:
            if error is ConnectionResetError:
                _log.warning(f"[ConnectionResetError] Cancelled ip:{self._client_addr}.", extra=self._ip)
            else:
                _log.warning(f"[TimeoutError] Cancelled ip:{self._client_addr}.", extra=self._ip)

            self._get_func_alive = False

    def __send_data(self):
        """get data from queue and send it to the other client"""
        self._send_func_alive = False
        _log.info("Send function start.", extra=self._ip)

        try:
            while True:

                if self._cache:
                    data = self._cache
                    self._cache = None
                else:
                    data = self._data_queue.get()
                    if data is RuntimeError:
                        _log.warning(f"[RuntimeError] Cancelled ip:{self._client_addr}.", extra=self._ip)
                        self._send_func_alive = False
                        break

                    self._to_client.sendall(data)

        except BrokenPipeError:
            self._cache = data  # No, it won't unless you say so.
            _log.warning(f"[BrokenPipeError] Cancelled ip:{self._client_addr}.", extra=self._ip)
            self._send_func_alive = False

        except ConnectionResetError:
            _log.warning(f"[ConnectionResetError] Cancelled ip:{self._client_addr}.", extra=self._ip)
            self._send_func_alive = False

    def start(self):
        while True:
            if not self._get_func_alive:
                self.__link_to_client()
                thread = threading.Thread(target=self.__get_data)
                thread.start()

            if not self._send_func_alive:
                try:
                    self.__get_to_client()
                except ClientOffLineError:
                    _log.warning("[ClientOffLineError] Continue.", extra=self._ip)
                    continue  # back to the origin

                thread = threading.Thread(target=self.__send_data)
                thread.start()

            while self._get_func_alive and self._send_func_alive:
                time.sleep(0.001)

    # TODO: Dose it work properly?
    def check_client_alive(self):
        """when both sides stop sending data and receiving data, it'll work"""
        while True:
            if self._data_queue.empty() and (self._get_func_alive or self._send_func_alive):
                time.sleep(5)

                if self._data_queue.empty() and (self._get_func_alive or self._send_func_alive):
                    try:
                        if hasattr(self._to_client, "send"):
                            self._to_client.send(b'\x00')
                        # what it sent is not necessary, we aim at checking whether client is still alive

                    except (ConnectionResetError, BrokenPipeError) as error:
                        _log.error(error, extra=self._ip)
                        #  then we'll stop functions which use the client
                        self._to_client.settimeout(1)  # Stop another get_func
                        self._data_queue.put(RuntimeError)  # Stop this send_func
                        time.sleep(1)
                        self._to_client.settimeout(None)

            time.sleep(5)
