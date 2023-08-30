class Buffer(object):

    def __init__(self):
        self._length: int = -1
        self._data_queue: list[bytes] = []
        self._total_data_size: int = 0

    def set_length(self, length: int) -> None:
        """set the size of the buffer if it is empty"""
        if not self._data_queue and length > 0:
            self._length = length
        elif length <= 0:
            raise ValueError(f"unexpected length: {length}")
        else:
            raise RuntimeError("data queue if not empty")

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

    def is_full(self) -> bool:
        """check if the buffer is full"""
        if self._total_data_size == self._length:
            return True
        else:
            return False

    def get(self) -> bytes | None:
        """return data in the buffer if it's full"""
        if self.is_full():
            self._total_data_size = 0
            data = b''.join(self._data_queue)
            self._data_queue.clear()

            return data

    @property
    def total_size(self) -> int:
        return self._total_data_size

    @property
    def length(self) -> int:
        return self._length
