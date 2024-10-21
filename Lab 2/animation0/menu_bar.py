import tkinter as tk
from tkinter import filedialog

from dynamic import DynamicMidiData
from message_passing import MessagePassing, LoadFile, UnloadFile
from threading import Lock

class LockingMenuState:
    def __init__(self):
        self.pending_close = False
        self.pending_open = False
        self.path = None
        self.lock = Lock()
    def update_path(self, path):
        with self.lock:
            self.pending_open = True
            self.path = path
    def on_close(self):
        with self.lock:
            self.pending_close = True
    def is_pending_close(self):
        with self.lock:
            return self.pending_close
    def is_pending_open(self):
        with self.lock:
            return self.pending_open
    def consume_close(self):
        with self.lock:
            self.pending_close = False
    def consume_path(self):
        with self.lock:
            self.pending_open = False
            path = self.path
            self.path = None
            return path

class MenuBar:
    def __init__(self, dynamic : DynamicMidiData, message_passing : MessagePassing, root : tk.Tk):
        self.root = root
        self.dynamic = dynamic
        self.message_passing = message_passing
        self.state = LockingMenuState()

        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.open_file)
        file_menu.add_command(label="Close File", command=self.close)
        file_menu.add_separator()
        file_menu.add_command(label="Exit Program", command=root.quit)

        menubar.add_cascade(label="Menu", menu=file_menu)
        root.config(menu=menubar)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            initialdir="resource/audio",
            filetypes=[("MIDI files", "*.mid *.midi")],
            title="Select a MIDI file"
        )
        if file_path:
            self.state.update_path(file_path)
    def close(self):
        self.state.on_close()
    def update(self, millis):
        if self.state.is_pending_open():
            path = self.state.consume_path()
            self._on_load_file(path)
        if self.state.is_pending_close():
            self.state.consume_close()
            self._close()
    def _on_load_file(self, path):
        self.message_passing.post_message(LoadFile(path))
    def _close(self):
        self.message_passing.post_message(UnloadFile())
