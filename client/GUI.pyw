import tkinter as tk
from tkinter import ttk

from client import conf, crypt_available
from host_main import start as h_start
from guest_main import start as v_start
from gui_component import *

HOST = "host"
GUEST = "guest"
OPTION = "option"


class MainWindow(tk.Tk):

    def __init__(self, title, size):
        super().__init__()

        self.title(title)
        self.geometry(size)

        self._task_manager = TaskManager(times=1, mutex=False)
        self._notebook = ttk.Notebook(self, width=20, height=20)
        self._str_var = {
            HOST: tk.StringVar(),
            GUEST: tk.StringVar(),
        }
        self._msg_pipe = {
            HOST: MessagePipe(),
            GUEST: MessagePipe(),
        }

        self._frame = {
            HOST: ClientFrame(self._task_manager, h_start, HOST, conf,
                              self._str_var[HOST], self._msg_pipe[HOST],
                              borderwidth=0),
            GUEST: ClientFrame(self._task_manager, v_start, GUEST, conf,
                               self._str_var[GUEST], self._msg_pipe[GUEST],
                               borderwidth=0),
            OPTION: OptionFrame(self._task_manager, conf, crypt_available, self._msg_pipe, borderwidth=1),
        }

        self._notebook.add(self._frame[HOST], text=HOST)
        self._notebook.add(self._frame[GUEST], text=GUEST)
        self._notebook.add(self._frame[OPTION], text=OPTION)
        self._notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = MainWindow("client", "600x400")
    root.mainloop()
