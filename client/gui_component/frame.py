from tkinter import ttk, messagebox
import tkinter as tk
import threading
import typing

from .message import Message
from .verify_tool import verify_ip, verify_port

HOST = "host"
GUEST = "guest"


class ClientFrame(ttk.Frame):

    def __init__(self, task_manager, func: typing.Callable, flag: str, conf,
                 msg_pipe, borderwidth: int):
        super().__init__(borderwidth=borderwidth)
        self.__task_manager = task_manager
        self.__msg_pipe = msg_pipe

        self.__bar = {
            tk.X: tk.Scrollbar(self, orient=tk.HORIZONTAL),
            tk.Y: tk.Scrollbar(self),
        }

        self.__text = Message(self, xscrollcommand=self.__bar[tk.X].set,
                              yscrollcommand=self.__bar[tk.Y].set, height=16, width=80, warp="none")

        if flag == HOST:
            args = *conf.get_func_args(HOST), self.__msg_pipe

        elif flag == GUEST:
            args = *conf.get_func_args(GUEST), self.__msg_pipe

        else:
            raise ValueError

        self.__task_manager.add_task(func, flag, args)

        self.__bar[tk.X].config(command=self.__text.xview)
        self.__bar[tk.Y].config(command=self.__text.yview)

        def start():
            self.__task_manager.run_task(flag)
            self.__text.write(f"run task[{flag}]")

        def cancel():
            self.__task_manager.cancel_task(flag)
            self.__text.write(f"cancel all the tasks[{flag}]")

        self._start_button = tk.Button(self, text="Start",
                                       command=start)
        self._cancel_button = tk.Button(self, text="Cancel",
                                        command=cancel)

        self.__pack_up()

        thd = threading.Thread(target=self.__get_msg, daemon=True)
        thd.start()

    def __pack_up(self):
        self.__bar[tk.X].pack(side=tk.BOTTOM, fill=tk.X)
        self.__bar[tk.Y].pack(side=tk.RIGHT, fill=tk.Y)

        self.__text.pack(side=tk.TOP, fill=tk.BOTH)

        self._start_button.pack(side=tk.LEFT, padx=60, pady=10)
        self._cancel_button.pack(side=tk.RIGHT, padx=60, pady=10)

    def __get_msg(self):
        total = ''
        while True:
            msg = self.__msg_pipe.read()
            total = ''.join([total, msg, ' '])
            self.__text.write(msg)


class OptionFrame(ttk.Frame):

    def __init__(self, task_manager, conf, crypto_available, msg_pipe, borderwidth):
        super().__init__(borderwidth=borderwidth)

        self.__task_manager = task_manager
        self.__var_int = tk.IntVar()
        self.conf = conf

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
            "guest": tk.Label(self, text="Guest options>"),
            "general": tk.Label(self, text="General options>")
        }

        self._save = {
            "apply": tk.Button(self, text="Apply",
                               command=self.__apply_conf),
            "save": tk.Button(self, text="Save",
                              command=self.__save_conf)
        }

        self.__init_option()

        if not crypto_available:
            self._check_button = tk.Checkbutton(self, text="Crypto", state="disabled")
        else:
            self._check_button = tk.Checkbutton(self, text="Crypto", variable=self.__var_int, onvalue=1, offvalue=0)

        if self.conf["crypt"]:
            self._check_button.select()
        else:
            self._check_button.deselect()

        self._check_button.grid(row=10, column=0)
        self._pipe = msg_pipe

    def __init_option(self):

        self._title[HOST].grid(row=0, column=0)
        self._title[GUEST].grid(row=4, column=0)
        self._title["general"].grid(row=9, column=0)

        self._h_option["open_port"]["label"].grid(row=1, column=0)
        self._h_option["open_port"]["entry"].grid(row=1, column=1)
        self._h_option["open_port"]["entry"].insert(0, self.conf[HOST, "open_port"])

        self._h_option["server_ip"]["label"].grid(row=2, column=0)
        self._h_option["server_ip"]["entry"].grid(row=2, column=1)
        self._h_option["server_ip"]["entry"].insert(0, self.conf[HOST, "server_address", "internet_ip"])

        self._h_option["server_port"]["label"].grid(row=3, column=0)
        self._h_option["server_port"]["entry"].grid(row=3, column=1)
        self._h_option["server_port"]["entry"].insert(0, self.conf[HOST, "server_address", "port"])

        self._v_option["open_port"]["label"].grid(row=5, column=0)
        self._v_option["open_port"]["entry"].grid(row=5, column=1)
        self._v_option["open_port"]["entry"].insert(0, self.conf[GUEST, "virtual_open_port"])

        self._v_option["server_ip"]["label"].grid(row=6, column=0)
        self._v_option["server_ip"]["entry"].grid(row=6, column=1)
        self._v_option["server_ip"]["entry"].insert(0, self.conf[GUEST, "server_address", "internet_ip"])

        self._v_option["server_port"]["label"].grid(row=7, column=0)
        self._v_option["server_port"]["entry"].grid(row=7, column=1)
        self._v_option["server_port"]["entry"].insert(0, self.conf[GUEST, "server_address", "port"])

        self._save["apply"].grid(row=11, column=0)
        self._save["save"].grid(row=11, column=1)

    def __apply_conf(self):
        try:
            self.__update_conf()

            self.__task_manager.set_args(HOST, *self.conf.get_func_args(HOST), self._pipe[HOST])
            self.__task_manager.set_args(GUEST, *self.conf.get_func_args(GUEST), self._pipe[GUEST])

            messagebox.showinfo(title="Info", message="Applied.")
        except ValueError as e:
            messagebox.showwarning(title="Warning", message=f"Invalid input: {e}.")

    def __save_conf(self):
        try:
            self.__update_conf()
            self.conf.save()

            messagebox.showinfo(title="Info", message="Saved.")
        except ValueError as e:
            messagebox.showwarning(title="Warning", message=f"Invalid input: {e}.")

    def __update_conf(self):
        value = self._h_option["open_port"]["entry"].get()
        if verify_port(value):
            self.conf.update(int(value), [HOST, "open_port"])

        value = self._h_option["server_ip"]["entry"].get()
        if verify_ip(value):
            self.conf.update(value, [HOST, "server_address", "internet_ip"])

        value = self._h_option["server_port"]["entry"].get()
        if verify_port(value):
            self.conf.update(int(value), [HOST, "server_address", "port"])

        value = self._v_option["open_port"]["entry"].get()
        if verify_port(value):
            self.conf.update(int(value), [GUEST, "virtual_open_port"])

        value = self._v_option["server_ip"]["entry"].get()
        if verify_ip(value):
            self.conf.update(value, [GUEST, "server_address", "internet_ip"])

        value = self._v_option["server_port"]["entry"].get()
        if verify_port(value):
            self.conf.update(int(value), [GUEST, "server_address", "port"])

        if self.__var_int.get() == 1:
            self.conf.update(True, ["crypt"])
        else:
            self.conf.update(False, ["crypt"])
