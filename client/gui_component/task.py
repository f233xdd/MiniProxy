import multiprocessing
import typing


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
                    print(f"mutex lock")
                    return -2  # not run for mutex

        if self._tasks[flag].running_count < self._max_t:
            if args or kwargs:
                self._tasks[flag].run(*args, **kwargs)
            else:
                self._tasks[flag].run(by_saved_args=True)

        else:
            print(f"tick lock")
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
