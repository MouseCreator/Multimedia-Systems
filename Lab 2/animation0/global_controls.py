import threading
class GlobalControls:
    def __init__(self):
        self.is_loaded = threading.Event()
        self.is_loaded.clear()
        self.is_playing = threading.Event()
        self.is_playing.clear()
        self.is_finished = threading.Event()
        self.is_finished.clear()