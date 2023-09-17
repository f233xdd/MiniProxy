# For the server
import queue
import socket
import threading
import logging

import queue_ex
import logging_ex

#  log config
log_length: bool | None = None
log_context: bool | None = None
_log: logging.Logger | None = None

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

                logging_ex.log_debug_msg(data, _log, log_length, log_context, extra=self._ip)

                if data:
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

                logging_ex.log_debug_msg(data, _log, log_length, log_context, extra=self._ip)

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
