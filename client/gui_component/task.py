import multiprocessing
import typing


class TaskManager:

    def __init__(self, times: int = 1, mutex: bool = True):
        self.__tasks: dict[str: Task] = {}

        self.__max_t: int = times
        self.__mutex: bool = mutex

    def add_task(self, func: typing.Callable, flag: str, args: tuple, kwargs: dict | None = None):
        if kwargs is None:
            kwargs = {}

        self.__tasks[flag] = Task(func, args, kwargs)

    def run_task(self, flag: str, *args, **kwargs):
        """start a process running on the task"""

        if self.__mutex:
            for k in self.__tasks.keys():
                if self.is_task_running(k) and k != flag:
                    print(f"mutex lock")
                    return -2  # not run for mutex

        if self.__tasks[flag].running_count < self.__max_t:
            if args or kwargs:
                self.__tasks[flag].run(*args, **kwargs)
            else:
                self.__tasks[flag].run(by_saved_args=True)

        else:
            print(f"tick lock")
            return -1  # not run for max tick

    def cancel_task(self, flag: int):
        """cancel all processes running on the task"""
        if self.is_task_running(flag):
            self.__tasks[flag].cancel()
        else:
            return -1  # not process is alive

    def set_args(self, flag, *args, **kwargs):
        self.__tasks[flag].set_args(*args, **kwargs)

    def is_task_running(self, flag: int) -> bool:
        if self.__tasks[flag].running_count != 0:
            return True
        else:
            return False


class Task:

    def __init__(self, func: typing.Callable, args: tuple = (), kwargs: dict | None = None):

        self.__func = func
        self.__args = args
        if kwargs is None:
            self.__kwargs = {}
        else:
            self.__kwargs = kwargs

        self.__run_count: int = 0
        self.__process: list[multiprocessing.Process] = []

    def run(self, by_saved_args: bool = False, *args, **kwargs):
        if by_saved_args:
            pcs = multiprocessing.Process(target=self.__func, args=self.__args, kwargs=self.__kwargs)
        else:
            pcs = multiprocessing.Process(target=self.__func, args=args, kwargs=kwargs)

        pcs.start()

        self.__process.append(pcs)
        self.__add_count()

    def cancel(self):
        """terminate all processes running"""
        for pcs in self.__process:
            pcs.terminate()

    def set_args(self, *args, **kwargs):
        """set default args"""
        if args:
            self.__args = args

        if kwargs:
            self.__kwargs = kwargs

    def __check_process_alive(self):
        """clean over processes and update process ticker"""
        i = 0
        while i < len(self.__process):
            if not self.__process[i].is_alive():
                del self.__process[i]
                self.__reduce_count()
                i += -1
            i += 1

    def __add_count(self):
        self.__run_count += 1

    def __reduce_count(self):
        self.__run_count += -1

    def __repr__(self):
        return f"{self.__run_count} | {self.__process}"

    @property
    def running_count(self) -> int:
        self.__check_process_alive()
        return self.__run_count
