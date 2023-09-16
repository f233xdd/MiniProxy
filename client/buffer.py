class Buffer(object):

    def __init__(self, static: bool = False, max_size: int | None = None):
        self._static: bool = static

        if max_size is not None:
            self._max_size: int | None = max_size
        else:
            self._max_size: int | None = -1

        self._data_queue: list[bytes] = []
        self._data_len: int = 0

    def set_length(self, length: int) -> None:
        """set the size of the buffer if it is empty"""
        if not self._static:
            if self.is_empty and (length > 0 or length == -1):
                self._max_size = length
            elif length <= 0:
                raise ValueError(f"unexpected length: {length}")
            else:
                raise RuntimeError("data queue is not empty")
        else:
            raise ValueError("Static buffer changed length.")

    def put(self, data: bytes, errors: str = "strict") -> bytes | None:
        """put data in the buffer and mark its length"""
        self._data_len += len(data)

        if self._data_len <= self._max_size:
            self._data_queue.append(data)

        else:
            if errors == "strict":
                msg = f"data length: {self._data_len} is over buffer max length: {self._max_size}"
                raise OverflowError(msg)

            elif errors == "return" or errors == "ignore":
                over = self._data_len - self._max_size

                self._data_queue.append(data[:-over])
                self._data_len = self._max_size

                if errors == "return":
                    return data[-over:]

            else:
                raise ValueError(f"unexpected errors: {errors}")

    def get(self, reset_len=False) -> bytes | None:
        """return data in the buffer if it's full"""
        if self.is_full:
            self._data_len = 0
            data = b''.join(self._data_queue)
            self._data_queue.clear()

            if reset_len:
                self.set_length(-1)

            return data

    @property
    def is_full(self) -> bool:
        """check if the buffer is full"""
        if self._data_len == self._max_size:
            return True
        else:
            return False

    @property
    def is_empty(self) -> bool:
        """return True if the buffer is empty"""
        if self._data_len == 0:
            return True
        else:
            return False

    @property
    def data_length(self) -> int:
        """return the data length of the buffer"""
        return self._data_len

    @property
    def size(self) -> int:
        """return the max length of the buffer"""
        return self._max_size

    def __repr__(self):
        """return buffer data for debug"""
        return str(b"".join(self._data_queue))
