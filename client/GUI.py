import time
import tkinter as tk
from tkinter.ttk import Notebook
import threading, logging


class GUI(tk.Tk):

    def __init__(self, title, size):
        super().__init__()

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

        self._host_bar = {
            'x': tk.Scrollbar(self._frame["host"], orient="horizontal"),
            'y': tk.Scrollbar(self._frame["host"]),
        }

        self._visitor_bar = {
            'x': tk.Scrollbar(self._frame["visitor"], orient="horizontal"),
            'y': tk.Scrollbar(self._frame["visitor"]),
        }

        self._host_bar['x'].pack(side="bottom", fill="x")
        self._host_bar['y'].pack(side="right", fill="y")
        self._visitor_bar['x'].pack(side="bottom", fill="x")
        self._visitor_bar['y'].pack(side="right", fill="y")

        self._host_text = MessageBox(self._frame["host"], xscrollcommand=self._host_bar['x'].set,
                                     yscrollcommand=self._host_bar['y'].set, height=20, width=80)

        self._visitor_text = MessageBox(self._frame["visitor"], xscrollcommand=self._visitor_bar['x'].set,
                                        yscrollcommand=self._visitor_bar['y'].set, height=20, width=80)

        self._host_bar['x'].config(command=self._host_text.xview)
        self._host_bar['y'].config(command=self._host_text.yview)
        self._visitor_bar['x'].config(command=self._visitor_text.xview)
        self._visitor_bar['y'].config(command=self._visitor_text.yview)

    def create_component(self):
        pass

    def show(self):
        # def h():
        #     for i in range(120):
        #         self._host_text.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%TEST%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        #
        # def v():
        #     for i in range(120):
        #         self._visitor_text.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%TEST%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        #
        # threading.Thread(target=h).start()
        # threading.Thread(target=v).start()
        self.mainloop()


class MessageBox(tk.Listbox):

    def __init__(self, master, xscrollcommand, yscrollcommand, height, width):
        super().__init__(master=master, xscrollcommand=xscrollcommand, yscrollcommand=yscrollcommand, height=height,
                         width=width)
        self._i = 0

        self.pack(side=tk.LEFT, fill=tk.BOTH)

    def write(self, msg):
        self.insert(tk.END, f"<l{self._i:0>3}\\> {msg}\n")

        self.update()
        self.see(tk.END)

        self._i += 1


root = GUI("client", "500x400")
root.show()
