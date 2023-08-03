import queue
import logging
import sys

_format_msg = "[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s"
_format_time = "%H:%M:%S"
_formatter = logging.Formatter(_format_msg, _format_time)

_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(_formatter)
_console.setLevel(logging.ERROR)

_log = logging.getLogger("QueueLog")
_log.addHandler(_console)
_log.setLevel(logging.ERROR)


class DoubleQueue(object):
    """It provide a exchange queue, suit for two."""

    def __init__(self):
        self._queue_1 = queue.Queue()
        self._queue_2 = queue.Queue()

        self._flag_1: int | None = None
        self._flag_2: int | None = None

    def add_flag(self, flag: int):
        if self._flag_1 is None:
            self._flag_1 = flag

        elif self._flag_2 is None:
            self._flag_2 = flag

        else:
            _log.error("MemoryError: Got more than two flags.")

    def put(self, data, flag: int, block: bool = True, timeout: float | None = None):
        if flag == self._flag_1:
            self._queue_1.put(data, block=block, timeout=timeout)

        elif flag == self._flag_2:
            self._queue_2.put(data, block=block, timeout=timeout)

        else:
            _log.error("ValueError: flag number is not correct.")
            _log.debug(f"_sign_1: {self._flag_1}, _sign_2: {self._flag_2}, input_sign: {flag}.")

    def get(self, flag: int, block: bool = True, timeout: float | None = None):
        if flag == self._flag_1:
            return self._queue_2.get(block=block, timeout=timeout)

        elif flag == self._flag_2:
            return self._queue_1.get(block=block, timeout=timeout)

        else:
            _log.error("ValueError: flag number is not correct.")
            _log.debug(f"_sign_1: {self._flag_1}, _sign_2: {self._flag_2}, input_sign: {flag}.")

    def empty(self, flag):
        if flag == self._flag_1:
            return self._queue_2.empty()

        elif flag == self._flag_2:
            return self._queue_1.empty()

        else:
            _log.error("ValueError: Flag number is not correct.")
            _log.debug(f"_flag_1: {self._flag_1}, _flag_2: {self._flag_2}, input_flag: {flag}.")


#  ready to test
class UmbrellaQueue(object):
    """It provide a exchange queue, suit for 3 or more."""

    def __init__(self):
        self._mapping: dict[int | str: queue.Queue] = {}
        self._root_queue = queue.Queue()
        self._root = None

    def add_queue(self, index, mode=None):
        if mode == "root":
            self._root = index
        else:
            self._mapping[index] = queue.Queue()

    def put(self, data, index, block=True, timeout=None):  # TODO: consider a generator?
        if index == self._root:
            for i in self._mapping.keys():
                self._mapping[i].put(data, block=block, timeout=timeout)
        else:
            self._root_queue.put(data, block=block, timeout=timeout)

    def get(self, index):  # TODO: consider a generator?
        if index == self._root:
            data = []
            for i in self._mapping.keys():
                try:
                    data.append(self._mapping[i].get(block=False))
                except queue.Empty:
                    pass
            if data:
                return data
        else:
            return self._root_queue.get(block=True)
