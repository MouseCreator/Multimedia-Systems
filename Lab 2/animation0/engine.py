import time
import threading
from itertools import count


class Engine:
    def __init__(self, root):
        self.root = root
        self.functions = []
        self.last_time = time.time()
        self.running = threading.Event()
        self.running.clear()
        self.count = 0
    def register(self, func):
        self.functions.append(func)
    def unregister(self, func):
        self.functions.remove(func)
    def clear(self):
        self.functions = []
        self.running.clear()
    def start(self):
        self.last_time = time.time()
        self.running.set()
        self._frame()
    def _frame(self):
        current_time = time.time()
        millis_since_last_frame = int((current_time - self.last_time) * 1000)
        for func in self.functions:
            func(millis_since_last_frame)
        self.last_time = current_time
        if self.running.is_set():
            self.root.after(16 - millis_since_last_frame, self._frame)

    def terminate(self):
        self.running.set()
