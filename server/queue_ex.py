import queue
import typing


class DoubleQueue(object):
    """It provide a exchange queue, suit for two."""

    def __init__(self):
        self._queue_1 = queue.Queue()
        self._queue_2 = queue.Queue()

        self._flag_1: int | None = None
        self._flag_2: int | None = None

    def add_flag(self, flag: int) -> None:
        if self._flag_1 is None:
            self._flag_1 = flag

        elif self._flag_2 is None:
            self._flag_2 = flag

        else:
            raise MemoryError("Got more than two flags.")

    def put(self, data, flag: int, exchange: bool = False, block: bool = True, timeout: float | None = None) -> None:
        if flag == self._flag_1:
            if exchange:
                self._queue_2.put(data, block=block, timeout=timeout)
            else:
                self._queue_1.put(data, block=block, timeout=timeout)

        elif flag == self._flag_2:
            if exchange:
                self._queue_1.put(data, block=block, timeout=timeout)
            else:
                self._queue_2.put(data, block=block, timeout=timeout)

        else:
            raise ValueError("flag number is not correct.")

    def get(self, flag: int, exchange: bool = False, block: bool = True, timeout: float | None = None) -> typing.Any:
        if flag == self._flag_1:
            if exchange:
                return self._queue_2.get(block=block, timeout=timeout)
            else:
                return self._queue_1.get(block=block, timeout=timeout)

        elif flag == self._flag_2:
            if exchange:
                return self._queue_1.get(block=block, timeout=timeout)
            else:
                return self._queue_2.get(block=block, timeout=timeout)

        else:
            raise ValueError("flag number is not correct.")

    def empty(self, flag, exchange: bool = False) -> bool:
        if flag == self._flag_1:
            if exchange:
                return self._queue_2.empty()
            else:
                return self._queue_1.empty()

        elif flag == self._flag_2:
            if exchange:
                return self._queue_1.empty()
            else:
                return self._queue_2.empty()

        else:
            raise ValueError("flag number is not correct.")

    def get_all(self, flag, exchange: bool = False) -> typing.Generator:
        if flag == self._flag_1:
            if exchange:
                while not self._queue_2.empty():
                    yield self._queue_2.get()
            else:
                while not self._queue_1.empty():
                    yield self._queue_1.get()

        elif flag == self._flag_2:
            if exchange:
                while not self._queue_1.empty():
                    yield self._queue_1.get()
            else:
                while not self._queue_2.empty():
                    yield self._queue_2.get()

        else:
            raise ValueError("flag number is not correct.")


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
