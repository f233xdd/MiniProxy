class Buffer(object):

    def __init__(self):
        self._length: int = -1
        self._data_queue: list[bytes] = []
        self._total_size: int = 0

    def set_length(self, length) -> None:
        """set the size of the buffer if it is empty"""
        if not self._data_queue:
            self._length = length

    def put(self, data) -> bytes | None:
        """put data in the buffer and mark its length"""
        self._total_size += len(data)

        if self._total_size <= self._length:
            self._data_queue.append(data)

        else:
            over = self._total_size - self._length

            self._data_queue.append(data[over:])
            self._total_size = self._length

            return data[:over]

    def is_full(self) -> bool:
        """check if the buffer is full"""
        if self._total_size == self._length:
            return True
        else:
            return False

    def get(self) -> bytes | None:
        """return data in the buffer if it's full"""
        if self.is_full():
            self._total_size = 0
            return b''.join(self._data_queue)

    @property
    def total_size(self) -> int:
        return self._total_size

    @property
    def length(self) -> int:
        return self._length