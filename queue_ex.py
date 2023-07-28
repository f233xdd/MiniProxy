import queue
import logging

format_msg = "[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s"
format_time = "%H:%M:%S"
formatter = logging.Formatter(format_msg, format_time)

file_handler = logging.FileHandler("queue.log", mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)

log = logging.getLogger("QueueLog")
log.addHandler(file_handler)


class DoubleQueue(object):
    """It provide a exchange queue, suit for 2."""

    def __init__(self):
        self._queue_1 = queue.Queue()
        self._queue_2 = queue.Queue()

        self._sign_1: int | None = None
        self._sign_2: int | None = None

    def add_sign(self, sign: int):
        if self._sign_1 is None:
            self._sign_1 = sign

        elif self._sign_2 is None:
            self._sign_2 = sign

        else:
            log.error("MemoryError: Got more than two signs.")

    def put(self, data, sign: int, block=True, timeout=None):
        if sign == self._sign_1:
            self._queue_1.put(data, block=block, timeout=timeout)

        elif sign == self._sign_2:
            self._queue_2.put(data, block=block, timeout=timeout)

        else:
            log.error("ValueError: Sign number is not correct.")
            log.debug(f"_sign_1: {self._sign_1}, _sign_2: {self._sign_2}, input_sign: {sign}.")

    def get(self, sign: int, block=True, timeout=None):
        if sign == self._sign_1:
            return self._queue_2.get(block=block, timeout=timeout)

        elif sign == self._sign_2:
            return self._queue_1.get(block=block, timeout=timeout)

        else:
            log.error("ValueError: Sign number is not correct.")
            log.debug(f"_sign_1: {self._sign_1}, _sign_2: {self._sign_2}, input_sign: {sign}.")


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
