
from abc import ABC, abstractmethod
import tkinter as tk
from typing import List

class GraphicKey:

    def __init__(self, parent: tk.Canvas, color: str):
        self.shape = parent.create_rectangle(0, 0, 40, 40, fill=color)
        self.parent = parent
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
    def press(self, apply_color=None):
        print("Key is pressed!")

    def release(self):
        print("Key is released!")

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.parent.coords(self.shape, self.x, self.y, self.x+self.width, self.y+self.height)
    def reload(self):
        pass
    def move(self, to_x, to_y):
        self.x = to_x
        self.y = to_y
        self.parent.move(self.shape, to_x, to_y)

    def apply_graphics(self, gparams):
        pass


class PianoKey:
    def __init__(self, index: int, visual: GraphicKey, color: str, normalized_position: int, notes: List[str]):
        self.index = index
        self.visual = visual
        self.color = color
        self.notes = notes
        self.normalized_position = normalized_position

    def on_raise(self, canvas: tk.Canvas):
        canvas.tag_raise(self.visual.shape)


class PianoParams:
    def __init__(self, total, white, black):
        self.keys_total = total
        self.keys_white = white
        self.keys_black = black

class PianoGraphicConfig:
    def __init__(self):
        self.white_overlay = None
        self.black_overlay = None
        self.black_normalized_x = 0.5
        self.black_normalized_y = 0.7

class Piano:
    def __init__(self, canvas: tk.Canvas, keys: List[PianoKey], pparams: PianoParams, gparams: PianoGraphicConfig):
        self.keys = keys
        self.pparams = pparams
        self.gparams = gparams
        self.canvas = canvas


    def resize(self, width, height):
        self.canvas.place(width=width,height=height)
        KeySizeCalculator.calculate_size(self, width, height)
    def clear_frame(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()


class KeyboardParams:
    def __init__(self, width, height, black_normalized_x=0.5, black_normalized_y=0.5):
        self.width = width
        self.height = height
        self.black_normalized_x = black_normalized_x
        self.black_normalized_y = black_normalized_y

class PianoCreatorEngine:

    def __init__(self, begin_with = 0, start_id=0):
        self.cycle = 12
        self.key_type = begin_with
        self.current_id = start_id
        self.black_keys = (1, 4, 6, 9, 11)

    def next_key(self):
        color = "black" if self.key_type in self.black_keys else "white"
        key = KeyPrototype(color, self.current_id)
        self.current_id += 1
        self.key_type += 1
        if self.key_type >= self.cycle:
            self.key_type = 0
        return key

class KeyPrototype:
    def __init__(self, color, identity):
        self.color = color
        self.identity = identity




class KeySizeCalculator:
    @staticmethod
    def calculate_size(piano: Piano, width: int, height: int):
        white_only = piano.pparams.keys_white
        white_width = width / white_only
        white_height = height
        black_width = white_width * piano.gparams.black_normalized_x
        black_height = white_height * piano.gparams.black_normalized_y
        for key in piano.keys:
            color = key.color
            if color == "white":
                key.visual.resize(white_width, white_height)
                new_x = key.normalized_position * white_width / 2
                key.visual.move(new_x, 0)
            else:
                key.visual.resize(black_width, black_height)
                new_x = key.normalized_position * white_width / 2
                key.visual.move(new_x, 0)

class PianoCreationParams:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
class PianoCreator(ABC):
    @abstractmethod
    def create_piano(self, root):
        pass

class PianoCreator88(PianoCreator):

    def create_piano(self, piano_params: PianoCreationParams) -> Piano:
        keys = []
        pparams = PianoParams(total=88, white=52, black=36)
        gparams = PianoGraphicConfig()
        engine = PianoCreatorEngine()

        position_pointer = 0
        canvas = tk.Canvas(piano_params.root, width=piano_params.width, height=piano_params.height)
        black_keys = []
        for i in range(0, 88):
            prototype_key = engine.next_key()
            index = prototype_key.identity
            color = prototype_key.color
            if color == "white":
                normalized_position = position_pointer
                visual = GraphicKey(canvas, "white")
            else:
                normalized_position = position_pointer - 0.25
                visual = GraphicKey(canvas, "black")
            notes = []
            actual_key = PianoKey(index, visual, color, normalized_position, notes)
            actual_key.visual.apply_graphics(gparams)
            keys.append(actual_key)
            if color == "white":
                position_pointer += 1
            else:
                black_keys.append(actual_key)

        piano = Piano(canvas, keys, pparams, gparams)
        for black_key in black_keys:
            black_key.on_raise(canvas)
        return piano