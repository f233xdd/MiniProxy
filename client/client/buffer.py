class Buffer(object):

    def __init__(self, static: bool = False, size: int | None = None):
        self._static: bool = static

        if size is None:
            if self._static:
                raise ValueError("static buffer has no size")

            else:
                self._size: int | None = size

        elif size > 0:
            self._size: int | None = size

        else:
            raise ValueError("unexpected init size")

        self._data_queue: list[bytes] = []
        self._data_len: int = 0

    def set_size(self, size: int | None) -> None:
        """set the size of the buffer if it is empty"""
        if not self._static:
            if self.is_empty and size is None:
                self._size = size
            elif self.is_empty and size > 0:
                self._size = size
            else:
                raise ValueError(f"unexpected size: {size}")
        else:
            raise ValueError("static buffer changed its size")

    def put(self, data: bytes, errors: str = "strict") -> bytes | None:
        """put data in the buffer and mark its length"""
        self._data_len += len(data)

        if self._data_len <= self._size:
            self._data_queue.append(data)

        else:
            if errors == "strict":
                msg = f"data length: {self._data_len} is over buffer max length: {self._size}"
                raise OverflowError(msg)

            elif errors == "return" or errors == "ignore":
                over = self._data_len - self._size

                self._data_queue.append(data[:-over])
                self._data_len = self._size

                if errors == "return":
                    return data[-over:]

            else:
                raise ValueError(f"unexpected errors: {errors}")

    def get(self, reset_size=False) -> bytes | None:
        """return data in the buffer if it's full"""
        if self.is_full:
            self._data_len = 0
            data = b''.join(self._data_queue)
            self._data_queue.clear()

            if reset_size:
                self.set_size(None)

            return data

    @property
    def is_full(self) -> bool:
        """check if it's full"""
        if self._data_len == self._size:
            return True
        else:
            return False

    @property
    def is_empty(self) -> bool:
        """check if it's empty"""
        if self._data_len:
            return False
        else:
            return True

    @property
    def data_length(self) -> int:
        """return the data length of the buffer"""
        return self._data_len

    @property
    def size(self) -> int:
        """return the max size of the buffer"""
        return self._size

    def __repr__(self):
        """return buffer data for debug"""
        return str(b"".join(self._data_queue))
