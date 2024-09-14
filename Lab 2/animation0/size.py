
class SizeTracker:
    def __init__(self, tracking):
        self.tracking = tracking
        self.functions = []
        self.time_to_extra_check = 100
        self.width, self.height = tracking.winfo_width(), tracking.winfo_height()
        self._func_id = None
        self._planned_action = False
    def register(self, func):
        self.functions.append(func)

    def bind_config(self):
        self._func_id = self.tracking.bind("<Configure>", self.on_resize)
    def on_resize(self, event):
        if event.widget  != self.tracking:
            return
        self.resize_to(event.width, event.height)
    def resize_to(self, width, height):
        self.width = width
        self.height = height
        for func in self.functions:
            func(self.width, self.height)
        if not self._planned_action:
            self._planned_action = True
            self.tracking.after(self.time_to_extra_check, self.extra_check)

    def extra_check(self):
        actual_width = self.tracking.winfo_width()
        actual_height = self.tracking.winfo_height()
        self.resize_to(actual_width, actual_height)
        self._planned_action = False
