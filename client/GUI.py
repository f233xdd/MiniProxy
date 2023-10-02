import threading
import tkinter as tk
from tkinter.ttk import Notebook

from host_main import main as h_main
from visitor_main import main as v_main


class GUI(tk.Tk):

    def __init__(self, title, size):
        super().__init__()
        self._task_manager = TaskManager(1, h_main, v_main)

        self.title(title)
        self.geometry(size)

        self._notebook = Notebook(self, width=20, height=20)

        self._frame = {
            "host": tk.Frame(),
            "visitor": tk.Frame(),
            "option": tk.Frame(),
        }

        self._notebook.add(self._frame["host"], text="host")
        self._notebook.add(self._frame["visitor"], text="visitor")
        self._notebook.add(self._frame["option"], text="options")
        self._notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self._h_bar = {
            tk.X: tk.Scrollbar(self._frame["host"], orient="horizontal"),
            tk.Y: tk.Scrollbar(self._frame["host"]),
        }

        self._v_bar = {
            tk.X: tk.Scrollbar(self._frame["visitor"], orient="horizontal"),
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

        self._h_button = tk.Button(self._frame["host"], text="start", command=lambda: self._task_manager.run(0))
        self._v_button = tk.Button(self._frame["visitor"], text="start", command=lambda: self._task_manager.run(1))
        self._h_button.pack(side=tk.BOTTOM)
        self._v_button.pack(side=tk.BOTTOM)

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
        self._threads: list[list[threading.Thread]] = []

        for t in task:
            self._tasks.append([t, 0])
            self._threads.append([])

        self._t = times
        self._lock = threading.Lock()

    def run(self, index):
        with self._lock:

            i = 0
            while i < len(self._threads[index]):
                if not self._threads[index][i].is_alive():
                    self._tasks[index][1] += -1
                    del self._threads[index][i]
                    i += -1
                i += 1

            if self._tasks[index][1] < self._t:
                thd = threading.Thread(target=self._tasks[index][0])
                self._threads[index].append(thd)
                thd.start()
                self._tasks[index][1] += 1

            else:
                return -1


if __name__ == "__main__":
    root = GUI("client", "600x400")
    root.show()
