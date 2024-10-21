import time
import threading


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
        while True:
            current_time = time.time()
            millis_since_last_frame = int((current_time - self.last_time) * 1000)
            for func in self.functions:
                func(millis_since_last_frame)
            self.last_time = current_time
            if self.running.is_set():
                wait = 16 - millis_since_last_frame
                if wait > 0:
                    self.root.after(wait, self._frame)
                    break

    def terminate(self):
        self.running.set()
