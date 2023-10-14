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

        self._task_manager = TaskManager(1, True, h_main, v_main)

        self.title(title)
        self.geometry(size)

        self._notebook = ttk.Notebook(self, width=20, height=20)

        self._frame = {
            HOST: tk.Frame(borderwidth=1),
            VISITOR: tk.Frame(borderwidth=1),
            OPTION: tk.Frame(borderwidth=1),
        }

        self._notebook.add(self._frame[HOST], text=HOST)
        self._notebook.add(self._frame[VISITOR], text=VISITOR)
        self._notebook.add(self._frame[OPTION], text=OPTION)
        self._notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        # host frame
        self._h_bar = {
            tk.X: tk.Scrollbar(self._frame[HOST], orient=tk.HORIZONTAL),
            tk.Y: tk.Scrollbar(self._frame[HOST]),
        }
        self._h_bar[tk.X].pack(side=tk.BOTTOM, fill=tk.X)
        self._h_bar[tk.Y].pack(side=tk.RIGHT, fill=tk.Y)

        self._h_text = Message(self._frame[HOST], xscrollcommand=self._h_bar[tk.X].set,
                               yscrollcommand=self._h_bar[tk.Y].set, height=16, width=80)

        self._h_bar[tk.X].config(command=self._h_text.xview)
        self._h_bar[tk.Y].config(command=self._h_text.yview)

        self._h_start_button = tk.Button(self._frame[HOST], text="Start",
                                         command=lambda: self._task_manager.run_task(0))
        self._h_cancel_button = tk.Button(self._frame[HOST], text="Cancel",
                                          command=lambda: self._task_manager.cancel_task(0))

        self._h_start_button.pack(side=tk.LEFT, padx=60, pady=10)
        self._h_cancel_button.pack(side=tk.RIGHT, padx=60, pady=10)
        # visitor frame
        self._v_bar = {
            tk.X: tk.Scrollbar(self._frame[VISITOR], orient=tk.HORIZONTAL),
            tk.Y: tk.Scrollbar(self._frame[VISITOR]),
        }

        self._v_bar[tk.X].pack(side=tk.BOTTOM, fill=tk.X)
        self._v_bar[tk.Y].pack(side=tk.RIGHT, fill=tk.Y)

        self._v_text = Message(self._frame[VISITOR], xscrollcommand=self._v_bar[tk.X].set,
                               yscrollcommand=self._v_bar[tk.Y].set, height=16, width=80)

        self._v_bar[tk.X].config(command=self._v_text.xview)
        self._v_bar[tk.Y].config(command=self._v_text.yview)

        self._v_start_button = tk.Button(self._frame[VISITOR], text="Start",
                                         command=lambda: self._task_manager.run_task(1))
        self._v_cancel_button = tk.Button(self._frame[VISITOR], text="Cancel",
                                          command=lambda: self._task_manager.cancel_task(1))

        self._v_start_button.pack(side=tk.LEFT, padx=60, pady=10)
        self._v_cancel_button.pack(side=tk.RIGHT, padx=60, pady=10)
        # option frame
        self._h_option = {  # TODO: get inputs
            "open_port": {"label": tk.Label(self._frame[OPTION], text="Open port"),
                          "entry": tk.Entry(self._frame[OPTION])},
            "server_ip": {"label": tk.Label(self._frame[OPTION], text="Server ip"),
                          "entry": tk.Entry(self._frame[OPTION])},
            "server_port": {"label": tk.Label(self._frame[OPTION], text="Server port"),
                            "entry": tk.Entry(self._frame[OPTION])},
        }

        self._v_option = {  # TODO: get inputs
            "open_port": {"label": tk.Label(self._frame[OPTION], text="Open port"),
                          "entry": tk.Entry(self._frame[OPTION])},
            "server_ip": {"label": tk.Label(self._frame[OPTION], text="Server ip"),
                          "entry": tk.Entry(self._frame[OPTION])},
            "server_port": {"label": tk.Label(self._frame[OPTION], text="Server port"),
                            "entry": tk.Entry(self._frame[OPTION])},
        }

        self._title = {
            "host": tk.Label(self._frame[OPTION], text="Host options>"),
            "visitor": tk.Label(self._frame[OPTION], text="Visitor options>"),
            "general": tk.Label(self._frame[OPTION], text="General options>")
        }

        self._save = {  # TODO: apply and save inputs
            "apply": tk.Button(self._frame[OPTION], text="Apply",
                               command=self.__apply_conf),
            "save": tk.Button(self._frame[OPTION], text="Save",
                              command=self.__save_conf)
        }

        self.__init_option()
        #  TODO: ensure whether module is installed
        self._check_button = tk.Checkbutton(self._frame[OPTION], text="Crypto",
                                            command=lambda: messagebox.showinfo(title="Info", message="Unavailable"))
        self._check_button.grid(row=10, column=0)

    def show(self):
        def h():
            for i in range(120):
                self._h_text.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%TEST%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        def v():
            for i in range(120):
                self._v_text.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%TEST%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        threading.Thread(target=h).start()
        threading.Thread(target=v).start()
        self.mainloop()

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

    def __update_conf(self):
        value = self._h_option["open_port"]["entry"].get()
        if value:
            client.conf.update(value, [HOST, "open_port"])

        value = self._h_option["server_ip"]["entry"].get()
        if value:
            client.conf.update(value, [HOST, "server_address", "internet_ip"])

        value = self._h_option["server_port"]["entry"].get()
        if value:
            client.conf.update(value, [HOST, "server_address", "port"])

        value = self._v_option["open_port"]["entry"].get()
        if value:
            client.conf.update(value, [VISITOR, "virtual_open_port"])

        value = self._v_option["server_ip"]["entry"].get()
        if value:
            client.conf.update(value, [VISITOR, "server_address", "internet_ip"])

        value = self._v_option["server_port"]["entry"].get()
        if value:
            client.conf.update(value, [VISITOR, "server_address", "port"])

    def __apply_conf(self):
        self.__update_conf()

        messagebox.showinfo(title="Info", message="Applied.")

    def __save_conf(self):
        self.__update_conf()
        client.conf.save()

        messagebox.showinfo(title="Info", message="Saved.")


class Message(tk.Listbox):

    def __init__(self, master, xscrollcommand, yscrollcommand, height, width):
        super().__init__(master=master, xscrollcommand=xscrollcommand, yscrollcommand=yscrollcommand, height=height,
                         width=width)
        self._i = 0

        self.pack(side=tk.TOP, fill=tk.BOTH)

    def write(self, msg):
        self.insert(tk.END, f"<L{self._i:0>3}\\> {msg}\n")

        self.update()
        self.see(tk.END)

        self._i += 1


class TaskManager:

    def __init__(self, times: int = 1, mutex: bool = True, *task: typing.Callable):
        self._tasks = []
        self._processes: list[list[multiprocessing.Process]] = []

        for t in task:
            self._tasks.append([t, 0])
            self._processes.append([])

        self._t = times
        self._mutex = mutex

    def __check_process(self):
        """clean over processes and update process ticker"""
        for i in range(len(self._tasks)):
            j = 0
            while j < len(self._processes[i]):
                if not self._processes[i][j].is_alive():
                    self._tasks[i][1] += -1
                    del self._processes[i][j]
                    j += -1
                j += 1

    def run_task(self, task: int):
        """start a process running on the task"""

        self.__check_process()

        if self._mutex:
            for i in range(len(self._tasks)):
                if (self._tasks[i][1] != 0) and i != task:
                    return -2

        if self._tasks[task][1] < self._t:
            pcs = multiprocessing.Process(target=self._tasks[task][0])
            self._processes[task].append(pcs)
            pcs.start()
            self._tasks[task][1] += 1

        else:
            return -1

    def cancel_task(self, task: int):
        """terminate all processes running on the task"""
        if self._tasks[task] != 0:
            for process in self._processes[task]:
                process.terminate()


if __name__ == "__main__":
    root = MainWindow("client", "600x400")
    root.show()
