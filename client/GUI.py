import multiprocessing
import threading
import tkinter as tk
from tkinter import ttk

from host_main import main as h_main
from visitor_main import main as v_main


class MainWindow(tk.Tk):

    def __init__(self, title, size):
        super().__init__()
        self._task_manager = TaskManager(1, h_main, v_main)

        self.title(title)
        self.geometry(size)

        self._notebook = ttk.Notebook(self, width=20, height=20)
        self._frame = {
            "host": tk.Frame(borderwidth=1),
            "visitor": tk.Frame(borderwidth=1),
            "option": tk.Frame(borderwidth=1),
        }

        self._notebook.add(self._frame["host"], text="host")
        self._notebook.add(self._frame["visitor"], text="visitor")
        self._notebook.add(self._frame["option"], text="options")
        self._notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self._h_bar = {
            tk.X: tk.Scrollbar(self._frame["host"], orient=tk.HORIZONTAL),
            tk.Y: tk.Scrollbar(self._frame["host"]),
        }

        self._v_bar = {
            tk.X: tk.Scrollbar(self._frame["visitor"], orient=tk.HORIZONTAL),
            tk.Y: tk.Scrollbar(self._frame["visitor"]),
        }

        self._h_bar[tk.X].pack(side=tk.BOTTOM, fill=tk.X)
        self._h_bar[tk.Y].pack(side=tk.RIGHT, fill=tk.Y)
        self._v_bar[tk.X].pack(side=tk.BOTTOM, fill=tk.X)
        self._v_bar[tk.Y].pack(side=tk.RIGHT, fill=tk.Y)

        self._h_text = MessageBox(self._frame["host"], xscrollcommand=self._h_bar[tk.X].set,
                                  yscrollcommand=self._h_bar[tk.Y].set, height=16, width=80)

        self._v_text = MessageBox(self._frame["visitor"], xscrollcommand=self._v_bar[tk.X].set,
                                  yscrollcommand=self._v_bar[tk.Y].set, height=16, width=80)

        self._h_bar[tk.X].config(command=self._h_text.xview)
        self._h_bar[tk.Y].config(command=self._h_text.yview)
        self._v_bar[tk.X].config(command=self._v_text.xview)
        self._v_bar[tk.Y].config(command=self._v_text.yview)

        self._h_start_button = tk.Button(self._frame["host"], text="start",
                                         command=lambda: self._task_manager.run_task(0))
        self._h_cancel_button = tk.Button(self._frame["host"], text="cancel",
                                          command=lambda: self._task_manager.cancel_task(0))
        self._v_start_button = tk.Button(self._frame["visitor"], text="start",
                                         command=lambda: self._task_manager.run_task(1))
        self._v_cancel_button = tk.Button(self._frame["visitor"], text="cancel",
                                          command=lambda: self._task_manager.cancel_task(1))

        self._h_start_button.pack(side="left", padx=60, pady=10)
        self._h_cancel_button.pack(side="right", padx=60, pady=10)
        self._v_start_button.pack(side="left", padx=60, pady=10)
        self._v_cancel_button.pack(side="right", padx=60, pady=10)

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


class MessageBox(tk.Listbox):

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

    def __init__(self, times: int = 1, *task):
        self._tasks = []
        self._processes: list[list[multiprocessing.Process]] = []

        for t in task:
            self._tasks.append([t, 0])
            self._processes.append([])

        self._t = times

    def run_task(self, task: int):
        i = 0
        while i < len(self._processes[task]):
            if not self._processes[task][i].is_alive():
                self._tasks[task][1] += -1
                del self._processes[task][i]
                i += -1
            i += 1

        if self._tasks[task][1] < self._t:
            thd = multiprocessing.Process(target=self._tasks[task][0])
            self._processes[task].append(thd)
            thd.start()
            self._tasks[task][1] += 1

        else:
            return -1

    def cancel_task(self, task: int):
        if self._tasks[task] != 0:
            for process in self._processes[task]:
                process.terminate()


if __name__ == "__main__":
    root = MainWindow("client", "600x400")
    root.show()
