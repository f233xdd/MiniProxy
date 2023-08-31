class Buffer(object):

    def __init__(self):
        self._length: int = -1
        self._data_queue: list[bytes] = []
        self._total_data_size: int = 0

    def set_length(self, length: int) -> None:
        """set the size of the buffer if it is empty"""
        if self.is_empty and length > 0:
            self._length = length
        elif length <= 0:
            raise ValueError(f"unexpected length: {length}")
        else:
            raise RuntimeError("data queue is not empty")

    def put(self, data: bytes, errors: str = "strict") -> bytes | None:
        """put data in the buffer and mark its length"""
        self._total_data_size += len(data)

        if self._total_data_size <= self._length:
            self._data_queue.append(data)

        else:
            if errors == "strict":
                raise OverflowError(f"data length: {self._total_data_size} is over buffer max length: {self._length}")

            elif errors == "return" or errors == "ignore":
                over = self._total_data_size - self._length

                self._data_queue.append(data[over:])
                self._total_data_size = self._length

                if errors == "return":
                    return data[:over]

            else:
                raise ValueError(f"unexpected errors: {errors}")

    def get(self, reset_len=False) -> bytes | None:
        """return data in the buffer if it's full"""
        if self.is_full:
            self._total_data_size = 0
            data = b''.join(self._data_queue)
            self._data_queue.clear()

            if reset_len:
                self._length = -1

            return data

    @property
    def is_full(self) -> bool:
        """check if the buffer is full"""
        if self._total_data_size == self._length:
            return True
        else:
            return False

    @property
    def is_empty(self) -> bool:
        if self._total_data_size == 0:
            return True
        else:
            return False

    @property
    def total_size(self) -> int:
        return self._total_data_size

    @property
    def length(self) -> int:
        return self._length
