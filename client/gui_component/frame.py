from tkinter import ttk, messagebox
import tkinter as tk
import threading
import typing

from .message import Message
from .infer_tool import verify_ip, verify_port

HOST = "host"
GUEST = "guest"


class ClientFrame(ttk.Frame):

    def __init__(self, task_manager, func: typing.Callable, flag: str, conf,
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
            args = *conf.get_func_args(HOST), self._msg_pipe

        elif flag == GUEST:
            args = *conf.get_func_args(GUEST), self._msg_pipe

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

        thd = threading.Thread(target=self.__get_msg, daemon=True)
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

    def __init__(self, task_manager, conf, crypto_available, msg_pipe, borderwidth):
        super().__init__(borderwidth=borderwidth)

        self._task_manager = task_manager
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
            self._check_button = tk.Checkbutton(self, text="Crypto")

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

            self._task_manager.set_args(HOST, *self.conf.get_func_args(HOST), self._pipe[HOST])
            self._task_manager.set_args(GUEST, *self.conf.get_func_args(GUEST), self._pipe[GUEST])
            # client._init_host_execute()
            # client._init_guest_execute()

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
