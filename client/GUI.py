import threading
import time
import tkinter as tk
from tkinter.ttk import Notebook


class GUI(tk.Tk):

    def __init__(self, title, size):
        super().__init__()

        self.title(title)
        self.geometry(size)

    def create_component(self):
        pass

    def show(self):
        self.mainloop()


class Text(tk.Text):

    def __init__(self, master, xscrollcommand, yscrollcommand):
        super().__init__(master=master, xscrollcommand=xscrollcommand, yscrollcommand=yscrollcommand)
        self._i = 0

        self.config(state=tk.DISABLED)
        self.pack(side=tk.LEFT, fill=tk.BOTH)

    def write(self, msg):
        self.config(state=tk.NORMAL)
        self.insert(tk.END, f"line:{self._i:0>3}|{msg}\n")
        self.config(state=tk.DISABLED)

        self.update()
        self.see(tk.END)

        self._i += 1


root = tk.Tk()
root.title("Client")
root.geometry("400x300")

notebook = Notebook(root, width=20, height=20)

host = tk.Frame()
visitor = tk.Frame()
option = tk.Frame()

host_x_bar = tk.Scrollbar(host)
host_y_bar = tk.Scrollbar(host, orient="horizontal")
visitor_msg = tk.Scrollbar(visitor)

host_x_bar.pack(side="right", fill="y")
host_y_bar.pack(side="bottom", fill="x")

visitor_msg.pack(side="right", fill="y")

text = Text(host, xscrollcommand=host_x_bar.set, yscrollcommand=host_x_bar.set)


def f():
    for i in range(120):
        time.sleep(1)
        text.write("qwq")


host_y_bar.config(command=text.xview)
host_x_bar.config(command=text.yview)

notebook.add(host, text="host")
notebook.add(visitor, text="visitor")
notebook.add(option, text="options")

notebook.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

threading.Thread(target=f).start()
root.mainloop()
