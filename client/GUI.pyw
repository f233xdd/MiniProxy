import multiprocessing
import threading
import typing
import tkinter as tk
from tkinter import ttk, messagebox

import client
from host_main import main as h_main
from visitor_main import main as v_main

HOST = "host"
VISITOR = "visitor"
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
            VISITOR: tk.StringVar(),
        }
        self._msg_pipe = {
            HOST: MessagePipe(),
            VISITOR: MessagePipe(),
        }

        self._frame = {
            HOST: ClientFrame(self._task_manager, h_main, HOST,
                              self._str_var[HOST], self._msg_pipe[HOST],
                              borderwidth=0),
            VISITOR: ClientFrame(self._task_manager, v_main, VISITOR,
                                 self._str_var[VISITOR], self._msg_pipe[VISITOR],
                                 borderwidth=0),
            OPTION: OptionFrame(self._task_manager, self._msg_pipe, borderwidth=1),
        }

        self._notebook.add(self._frame[HOST], text=HOST)
        self._notebook.add(self._frame[VISITOR], text=VISITOR)
        self._notebook.add(self._frame[OPTION], text=OPTION)
        self._notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)


class ClientFrame(ttk.Frame):

    def __init__(self, task_manager, func: typing.Callable, flag: str,
                 str_var: tk.StringVar, msg_pipe, borderwidth: int):
        super().__init__(borderwidth=borderwidth)
        self._task_manager = task_manager
        self._msg_pipe = msg_pipe
        self._txt_var = str_var

        self._bar = {
            tk.X: tk.Scrollbar(self, orient=tk.HORIZONTAL),
            tk.Y: tk.Scrollbar(self),
        }

        self._text = Message(self, xscrollcommand=self._bar[tk.X].set,
                             yscrollcommand=self._bar[tk.Y].set, height=16, width=80, warp="none")

        if flag == HOST:
            args = *client.conf.get_func_args(HOST), self._msg_pipe

        elif flag == VISITOR:
            args = *client.conf.get_func_args(VISITOR), self._msg_pipe

        else:
            raise ValueError

        self._task_manager.add_task(func, flag, args)

        self._bar[tk.X].config(command=self._text.xview)
        self._bar[tk.Y].config(command=self._text.yview)

        self._start_button = tk.Button(self, text="Start",
                                       command=lambda: self._task_manager.run_task(flag))
        self._cancel_button = tk.Button(self, text="Cancel",
                                        command=lambda: self._task_manager.cancel_task(flag))

        self.__pack_up()

        thd = threading.Thread(target=self.__get_msg)
        thd.start()

    def __pack_up(self):
        self._bar[tk.X].pack(side=tk.BOTTOM, fill=tk.X)
        self._bar[tk.Y].pack(side=tk.RIGHT, fill=tk.Y)

        self._text.pack(side=tk.TOP, fill=tk.BOTH)

        self._start_button.pack(side=tk.LEFT, padx=60, pady=10)
        self._cancel_button.pack(side=tk.RIGHT, padx=60, pady=10)

    def __get_msg(self):
        total = ''
        while True:
            msg = self._msg_pipe.read()
            total = ''.join([total, msg, ' '])

            self._text.write(msg)


class OptionFrame(ttk.Frame):

    def __init__(self, task_manager, msg_pipe, borderwidth):
        super().__init__(borderwidth=borderwidth)

        self._task_manager = task_manager

        self._h_option = {
            "open_port": {"label": tk.Label(self, text="Open port"),
                          "entry": tk.Entry(self)},
            "server_ip": {"label": tk.Label(self, text="Server ip"),
                          "entry": tk.Entry(self)},
            "server_port": {"label": tk.Label(self, text="Server port"),
                            "entry": tk.Entry(self)},
        }

        self._v_option = {
            "open_port": {"label": tk.Label(self, text="Open port"),
                          "entry": tk.Entry(self)},
            "server_ip": {"label": tk.Label(self, text="Server ip"),
                          "entry": tk.Entry(self)},
            "server_port": {"label": tk.Label(self, text="Server port"),
                            "entry": tk.Entry(self)},
        }

        self._title = {
            "host": tk.Label(self, text="Host options>"),
            "visitor": tk.Label(self, text="Visitor options>"),
            "general": tk.Label(self, text="General options>")
        }

        self._save = {
            "apply": tk.Button(self, text="Apply",
                               command=self.__apply_conf),
            "save": tk.Button(self, text="Save",
                              command=self.__save_conf)
        }

        self.__init_option()
        #  TODO: ensure whether module is installed
        self._check_button = tk.Checkbutton(self, text="Crypto",
                                            command=lambda: messagebox.showinfo(title="Info", message="Unavailable"))

        self._check_button.grid(row=10, column=0)
        self._pipe = msg_pipe

    def __init_option(self):

        self._title[HOST].grid(row=0, column=0)
        self._title[VISITOR].grid(row=4, column=0)
        self._title["general"].grid(row=9, column=0)

        self._h_option["open_port"]["label"].grid(row=1, column=0)
        self._h_option["open_port"]["entry"].grid(row=1, column=1)
        self._h_option["open_port"]["entry"].insert(0, client.conf[HOST, "open_port"])

        self._h_option["server_ip"]["label"].grid(row=2, column=0)
        self._h_option["server_ip"]["entry"].grid(row=2, column=1)
        self._h_option["server_ip"]["entry"].insert(0, client.conf[HOST, "server_address", "internet_ip"])

        self._h_option["server_port"]["label"].grid(row=3, column=0)
        self._h_option["server_port"]["entry"].grid(row=3, column=1)
        self._h_option["server_port"]["entry"].insert(0, client.conf[HOST, "server_address", "port"])

        self._v_option["open_port"]["label"].grid(row=5, column=0)
        self._v_option["open_port"]["entry"].grid(row=5, column=1)
        self._v_option["open_port"]["entry"].insert(0, client.conf[VISITOR, "virtual_open_port"])

        self._v_option["server_ip"]["label"].grid(row=6, column=0)
        self._v_option["server_ip"]["entry"].grid(row=6, column=1)
        self._v_option["server_ip"]["entry"].insert(0, client.conf[VISITOR, "server_address", "internet_ip"])

        self._v_option["server_port"]["label"].grid(row=7, column=0)
        self._v_option["server_port"]["entry"].grid(row=7, column=1)
        self._v_option["server_port"]["entry"].insert(0, client.conf[VISITOR, "server_address", "port"])

        self._save["apply"].grid(row=11, column=0)
        self._save["save"].grid(row=11, column=1)

    def __apply_conf(self):
        try:
            self.__update_conf()

            self._task_manager.set_args(HOST, *client.conf.get_func_args(HOST), self._pipe[HOST])
            self._task_manager.set_args(VISITOR, *client.conf.get_func_args(VISITOR), self._pipe[VISITOR])
            # client._init_host_execute()
            # client._init_visitor_execute()

            messagebox.showinfo(title="Info", message="Applied.")
        except ValueError as e:
            messagebox.showwarning(title="Warning", message=f"Invalid input: {e}.")

    def __save_conf(self):
        try:
            self.__update_conf()
            client.conf.save()

            messagebox.showinfo(title="Info", message="Saved.")
        except ValueError as e:
            messagebox.showwarning(title="Warning", message=f"Invalid input: {e}.")

    def __update_conf(self):
        value = self._h_option["open_port"]["entry"].get()
        if verify_port(value):
            client.conf.update(int(value), [HOST, "open_port"])

        value = self._h_option["server_ip"]["entry"].get()
        if verify_ip(value):
            client.conf.update(value, [HOST, "server_address", "internet_ip"])

        value = self._h_option["server_port"]["entry"].get()
        if verify_port(value):
            client.conf.update(int(value), [HOST, "server_address", "port"])

        value = self._v_option["open_port"]["entry"].get()
        if verify_port(value):
            client.conf.update(int(value), [VISITOR, "virtual_open_port"])

        value = self._v_option["server_ip"]["entry"].get()
        if verify_ip(value):
            client.conf.update(value, [VISITOR, "server_address", "internet_ip"])

        value = self._v_option["server_port"]["entry"].get()
        if verify_port(value):
            client.conf.update(int(value), [VISITOR, "server_address", "port"])


class Message(tk.Text):

    def __init__(self, master, xscrollcommand, yscrollcommand, height, width, warp):
        super().__init__(master=master, xscrollcommand=xscrollcommand, yscrollcommand=yscrollcommand, height=height,
                         width=width, wrap=warp, font=('Ubuntu Mono', 13, ''))

        self.config(state=tk.DISABLED)
        self._i = 0

    def write(self, msg):
        self.config(state=tk.NORMAL)

        self.insert(tk.END, f"{self._i:0>3}| {msg}")
        self.update()

        self.config(state=tk.DISABLED)
        self.see(tk.END)

        self._i += 1


class TaskManager:

    def __init__(self, times: int = 1, mutex: bool = True):
        self._tasks: dict[str: Task] = {}

        self._max_t: int = times
        self._mutex: bool = mutex

    def add_task(self, func: typing.Callable, flag: str, args: tuple, kwargs: dict | None = None):
        if kwargs is None:
            kwargs = {}

        self._tasks[flag] = Task(func, args, kwargs)

    def run_task(self, flag: str, *args, **kwargs):
        """start a process running on the task"""

        if self._mutex:
            for k in self._tasks.keys():
                if self.is_task_running(k) and k != flag:
                    print(f"mutex: {flag}")
                    return -2  # not run for mutex

        if self._tasks[flag].running_count < self._max_t:
            if args or kwargs:
                self._tasks[flag].run(*args, **kwargs)
            else:
                self._tasks[flag].run(by_saved_args=True)

        else:
            print(f"count: {flag}, {self._max_t}, {self._tasks[flag]}")
            return -1  # not run for max tick

    def cancel_task(self, flag: int):
        """cancel all processes running on the task"""
        if self.is_task_running(flag):
            self._tasks[flag].cancel()

    def set_args(self, flag, *args, **kwargs):
        self._tasks[flag].set_args(*args, **kwargs)

    def is_task_running(self, flag: int) -> bool:
        if self._tasks[flag].running_count != 0:
            return True
        else:
            return False


class Task:

    def __init__(self, func: typing.Callable, args: tuple = (), kwargs: dict | None = None):

        self._func = func
        self._args = args
        if kwargs is None:
            self._kwargs = {}
        else:
            self._kwargs = kwargs

        self._run_count: int = 0
        self._process: list[multiprocessing.Process] = []

    def run(self, by_saved_args: bool = False, *args, **kwargs):
        if by_saved_args:
            pcs = multiprocessing.Process(target=self._func, args=self._args, kwargs=self._kwargs)
        else:
            pcs = multiprocessing.Process(target=self._func, args=args, kwargs=kwargs)

        pcs.start()

        self._process.append(pcs)
        self.__add_count()

    def cancel(self):
        """terminate all processes running"""
        for pcs in self._process:
            pcs.terminate()

    def set_args(self, *args, **kwargs):
        """set default args"""
        if args:
            self._args = args

        if kwargs:
            self._kwargs = kwargs

    def __check_process_alive(self):
        """clean over processes and update process ticker"""
        i = 0
        while i < len(self._process):
            if not self._process[i].is_alive():
                del self._process[i]
                self.__reduce_count()
                i += -1
            i += 1

    def __add_count(self):
        self._run_count += 1

    def __reduce_count(self):
        self._run_count += -1

    def __repr__(self):
        return f"{self._run_count} | {self._process}"

    @property
    def running_count(self) -> int:
        self.__check_process_alive()
        return self._run_count


class MessagePipe:

    def __init__(self):
        self._queue = multiprocessing.Queue()

    def write(self, msg):
        self._queue.put(msg)

    def read(self, block: bool = True):
        return self._queue.get(block=block)


def verify_ip(ip: str) -> bool:
    if isinstance(ip, str):
        sep_str = ip.split('.')

        if len(sep_str) == 4:
            try:
                for s in sep_str:
                    if not 0 <= int(s) <= 999:
                        return False
                return True
            except ValueError:
                pass

    raise ValueError(ip)


def verify_port(port: str) -> bool:
    if isinstance(port, str):
        try:
            if 0 <= int(port) <= 65535:
                return True
        except ValueError:
            pass

    raise ValueError(port)


if __name__ == "__main__":
    root = MainWindow("client", "600x400")
    root.mainloop()
