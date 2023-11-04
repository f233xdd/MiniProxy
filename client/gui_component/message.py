import tkinter as tk
import multiprocessing


class Message(tk.Text):

    def __init__(self, master, xscrollcommand, yscrollcommand, height, width, warp):
        super().__init__(master=master, xscrollcommand=xscrollcommand, yscrollcommand=yscrollcommand, height=height,
                         width=width, wrap=warp, font=('Ubuntu Mono', 13, ''))

        self.config(state=tk.DISABLED)
        self._i = 0

    def write(self, msg: str, end: str = "\n"):
        msg = msg.strip()
        self.config(state=tk.NORMAL)

        self.insert(tk.END, f"{self._i:0>3}| {msg}{end}")
        self.update()

        self.config(state=tk.DISABLED)
        self.see(tk.END)

        self._i += 1


class MessagePipe:

    def __init__(self):
        self._queue = multiprocessing.Manager().Queue()
        # self._queue = multiprocessing.Queue()

    def write(self, msg):
        self._queue.put(msg)

    def read(self, block: bool = True):
        msg = self._queue.get(block=block)
        return msg

    def __repr__(self):
        return "MessagePipe: " + self._queue.__repr__()
