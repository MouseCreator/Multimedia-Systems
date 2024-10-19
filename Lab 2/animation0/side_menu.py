import tkinter as tk
from tkinter import colorchooser

from PIL.ImImagePlugin import number

from dynamic import DynamicMidiData, Defaults


class ColorChoosingComponent:
    def __init__(self, channel_id : int, current_color):
        self.number = channel_id
        self.current_color = current_color
        self.color_graphic = None
    def choose_color(self):
        color_code = colorchooser.askcolor(title=f"Channel {number} color")
        self.current_color = color_code
        # update_global_colors(channel, color)

class SideMenu:

    def __init__(self, parent: tk.Frame, dynamics : DynamicMidiData):
        self.dynamics = dynamics
        self.color_pickers = []
        for i in range(Defaults.channel_count()):
            self.color_pickers.append(ColorChoosingComponent(i, dynamics.channel_colors[i]))


