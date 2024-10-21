import threading
import tkinter as tk
from abc import abstractmethod
from tkinter import ttk, Button
from tkinter import colorchooser

from abc import ABC

from dynamic import DynamicMidiData, Defaults
from global_controls import GlobalControls
from message_passing import MessagePassing, ChannelColorMessage, TickMessage, LengthMessage


class SliderComponent(ABC):
    def __init__(self, parent : tk.Frame, scale : tk.Scale):
        self.root = parent
        self.scale = scale
        self.moving = False
        self.last_value = None
        self.timer = None
        self.scale.bind("<B1-Motion>", self._when_started_moving)
        self.scale.bind("<ButtonRelease-1>", self._check_stop_moving)

    def _when_started_moving(self, event):
        if not self.moving:
            self.moving = True

        if self.timer is not None:
            self.root.after_cancel(self.timer)
        self._on_start()

    @abstractmethod
    def _on_start(self):
        pass
    @abstractmethod
    def _on_end(self, new_value):
        pass
    def _check_stop_moving(self, event):
        if self.moving:
            self.timer = self.root.after(20, self._when_stopped_moving)

    def _when_stopped_moving(self):
        cursor_value = self.scale.get()
        self.moving = False
        self.timer = None
        self._on_end(cursor_value)
    def is_moving(self):
        return self.moving
    def current_value(self) -> int:
        return int(self.scale.get())

class TimelineSlider(SliderComponent):
    def _on_start(self):
        self.tracking = False
    def __init__(self, parent, scale):
        super().__init__(parent, scale)
        self.was_paused = False
        self.tracking = True
        self.just_moved_flag = threading.Event()
        self.just_moved_flag.clear()
        self.last_move_to_pos = None
    def _on_end(self, new_value):
        self.tracking = True
        self.just_moved_flag.set()
        self.last_move_to_pos = new_value
    def set_value(self, new_value):
        self.scale.set(new_value)
    def should_track(self):
        return self.tracking
    def just_moved(self) -> True:
        return self.just_moved_flag.is_set()
    def consume(self) -> int | None:
        self.just_moved_flag.clear()
        return self.last_move_to_pos

class LookaheadSlider(SliderComponent):
    def _on_start(self):
        pass
    def __init__(self, parent, scale):
        super().__init__(parent, scale)
        self.just_moved_flag = threading.Event()
        self.just_moved_flag.clear()
        self.last_move_to_pos = None
    def _on_end(self, new_value):
        self.just_moved_flag.set()
        self.last_move_to_pos = new_value
    def just_moved(self) -> True:
        return self.just_moved_flag.is_set()
    def consume(self) -> int | None:
        self.just_moved_flag.clear()
        return self.last_move_to_pos


class SideMenu:
    btn : tk.Button
    btn2 : tk.Button
    def __init__(self, parent: tk.Frame, global_c : GlobalControls, dynamics: DynamicMidiData, message_passing : MessagePassing):
        self.parent = parent
        self.dynamics = dynamics
        self.global_c = global_c
        self.message_passing = message_passing
        self.color_buttons = []
        self.color_frames = []
        self.canvas = tk.Canvas(self.parent)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.create(self.scrollable_frame)
    def update(self, millis):
        self._read_messages()

        if self.lookahead.just_moved():
            new_lookahead = self.lookahead.consume()
            self.message_passing.post_message(LengthMessage(new_lookahead))

        if self.global_c.is_playing.is_set():
            if self.timeline.just_moved():
                val = self.timeline.consume()
                self.message_passing.post_message(TickMessage(val))
            elif self.timeline.should_track():
                self.timeline.set_value(self.dynamics.current_tick)
    def _read_messages(self):
        if self.message_passing.pop_message("finish") is not None:
            self.btn.config(text="Finish")
        if self.message_passing.pop_message("sidebar") is not None:
            self.btn.config(text="Play")
            for i in range(0, Defaults.channel_count()):
                self.color_frames[i] = self.dynamics.channel_colors[i]
            self.slider.config(from_=Defaults.time_before(),to=self.dynamics.duration_ticks)
            self.timeline.set_value(Defaults.time_before())
    def create(self, parent):
        self.top_frame = tk.Frame(parent)
        self.top_frame.grid(row=0, column=0, padx=1, pady=1)
        self.bottom_frame = tk.Frame(parent)
        self.bottom_frame.grid(row=1, column=0, padx=1, pady=1)
        self.slider = tk.Scale(self.top_frame, from_=0, to=0, length=150, orient='horizontal')
        self.slider.grid(row=0, column=1, padx=5, pady=5)
        self.timeline = TimelineSlider(self.top_frame, self.slider)
        self.btn = tk.Button(self.top_frame, width=8, text="Pause",command=self._toggle_pause)
        self.btn.grid(row=0, column=2, padx=5, pady=5)

        self.note_size_slider = tk.Scale(self.top_frame, from_=1, to=20, orient='horizontal')
        self.note_size_slider.set(2)

        self.lookahead = LookaheadSlider(self.top_frame, self.note_size_slider)

        self.note_size_slider.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.label1 = tk.Label(self.top_frame, text="Note Size")
        self.label1.grid(row=1, column=2, padx=5, pady=5)

        for i in range(16):
            color_frame = tk.Frame(self.bottom_frame, width=10, height=10, bg=self.dynamics.channel_colors[i], bd=1, relief="solid")
            color_button = tk.Button(self.bottom_frame, text=f"Channel {i}", command=lambda cn=i: self._pick_color(cn))
            color_frame.grid(row=2 + i // 2, column=i % 2 * 2, padx=5, pady=5)
            color_button.grid(row=2 + i // 2, column=i % 2 * 2 + 1, padx=5, pady=5)
            self.color_buttons.append(color_button)
            self.color_frames.append(color_frame)

    def _toggle_pause(self):
        if self.global_c.is_playing.is_set():
            self.global_c.is_playing.clear()
            self.btn.config(text="Play")
        else:
            self.global_c.is_playing.set()
            self.btn.config(text="Pause")
    @staticmethod
    def _validate_numeric_input(new_value):
        if new_value.isdigit() or new_value == "":
            return True
        else:
            return False
    def _pick_color(self, channel_number: int):
        color = colorchooser.askcolor(title=f"Choose a color for channel {channel_number}")
        if not color:
            return
        hex_color = color[1]
        self.dynamics.channel_colors[channel_number] = hex_color
        self.color_frames[channel_number].config(bg=hex_color)
        self.message_passing.post_message(ChannelColorMessage(channel_number))


