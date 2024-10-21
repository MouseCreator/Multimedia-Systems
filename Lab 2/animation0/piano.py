from abc import ABC, abstractmethod
import tkinter as tk
from typing import List

from dynamic import DynamicMidiData
from midis import SoundEvent
import utils

class GraphicKey:

    def __init__(self, parent: tk.Canvas, index : int, color: str, dynamic : DynamicMidiData):
        self.shape = parent.create_rectangle(0, 0, 40, 40, fill=color)
        self.parent = parent
        self.x = 0
        self.y = 0
        self.index = index
        self.width = 0
        self.height = 0
        self.dynamics = dynamic
        self.original_color = color
        self.channel_stack = []

    def press(self, channel : int):
        self.channel_stack.append(channel)
        color = self.dynamics.channel_colors[channel]
        self.parent.itemconfig(self.shape, fill=color)
    def update_color(self):
        if not self.channel_stack:
            return
        last = self.channel_stack[len(self.channel_stack)-1]
        color = self.dynamics.channel_colors[last]
        self.parent.itemconfig(self.shape, fill=color)
    def release(self, channel):
        last_index = utils.last_index_of(self.channel_stack, channel)
        if last_index == -1:
            raise Exception(f"Cannot release channel with index {channel}")
        self.channel_stack.pop(last_index)

        last_index = len(self.channel_stack) - 1
        if last_index == -1:
            self.parent.itemconfig(self.shape, fill=self.original_color)
            return
        new_channel = self.channel_stack[last_index]
        new_color = self.dynamics.channel_colors[new_channel]
        self.parent.itemconfig(self.shape, fill=new_color)
    def to_original_color(self):
        self.channel_stack.clear()
        self.parent.itemconfig(self.shape, fill=self.original_color)

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

    def on_press(self, channel: int):
        self.visual.press(channel)

    def on_release(self, channel: int):
        self.visual.release(channel)

    def to_initial_state(self):
        self.visual.to_original_color()


class PianoParams:
    def __init__(self, total, white, black):
        self.keys_total = total
        self.keys_white = white
        self.keys_black = black

class PianoGraphicConfig:
    def __init__(self):
        self.black_normalized_x = 0.5
        self.black_normalized_y = 0.7

class DynamicGraphicalParams:
    def __init__(self):
        self.white_width = 0
        self.black_width = 0
        self.white_height = 0
        self.black_height = 0

class NotesMap:
    def __init__(self):
        self.note_map = {}

    def when_pressed(self, note_to_play):
        return self.note_map[note_to_play]

    def put(self, note_id, key_id):
        self.note_map[note_id] = key_id


class Piano:
    dynamic_gfx : DynamicGraphicalParams
    def __init__(self,
                 canvas: tk.Canvas,
                 dynamic : DynamicMidiData,
                 keys: List[PianoKey],
                 pparams: PianoParams,
                 gparams: PianoGraphicConfig,
                 note_map : NotesMap):
        self.keys = keys
        self.pparams = pparams
        self.gparams = gparams
        self.canvas = canvas
        self.dynamic = dynamic
        self.note_map = note_map
        self.dynamic_gfx = DynamicGraphicalParams()


    def resize(self, width, height):
        self.canvas.place(width=width,height=height)
        KeySizeCalculator.calculate_size(self, width, height)
    def clear_frame(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()

    def press(self, note_to_play : SoundEvent):
        key_index = self.note_map.when_pressed(note_to_play.note)
        key = self.keys[key_index]
        key.on_press(note_to_play.channel)

    def release(self, note_to_release : SoundEvent):
        key_index = self.note_map.when_pressed(note_to_release.note)
        key = self.keys[key_index]
        key.on_release(note_to_release.channel)
    def key_id_of(self, target_note : SoundEvent) -> PianoKey:
        key_index = self.note_map.when_pressed(target_note.note)
        return self.keys[key_index]

    def release_all(self):
        for key in self.keys:
            key.to_initial_state()

    def update_colors(self):
        for key in self.keys:
            key.visual.update_color()


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
        piano.dynamic_gfx.white_width = white_width
        piano.dynamic_gfx.black_width = black_width
        piano.dynamic_gfx.white_height = white_height
        piano.dynamic_gfx.black_height = black_height
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
    def create_piano(self, dynamic : DynamicMidiData,  params : PianoCreationParams) -> Piano:
        pass

class PianoCreator88(PianoCreator):
    @staticmethod
    def create_note_map() -> NotesMap:
        notes_map = NotesMap()
        beginning_maps_to = [1,2,3,4,5,6,7,8,9,10,11,0]
        beginning_len = len(beginning_maps_to)
        for i in range(0, 21):
            notes_map.put(i, beginning_maps_to[i % beginning_len])
        for i in range(21, 109):
            notes_map.put(i, i - 21)
        ending_maps_to = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108]
        ending_len = len(ending_maps_to)
        for i in range(109, 128):
            notes_map.put(i, ending_maps_to[i % ending_len])
        return notes_map

    def create_piano(self, dynamic : DynamicMidiData,
                     piano_params: PianoCreationParams) -> Piano:
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
                visual = GraphicKey(canvas, i,"white", dynamic)
            else:
                normalized_position = position_pointer - 0.25
                visual = GraphicKey(canvas, i,"black", dynamic)
            notes = []
            actual_key = PianoKey(index, visual, color, normalized_position, notes)
            actual_key.visual.apply_graphics(gparams)
            keys.append(actual_key)
            if color == "white":
                position_pointer += 1
            else:
                black_keys.append(actual_key)
        notes_map = PianoCreator88.create_note_map()
        piano = Piano(canvas, dynamic, keys, pparams, gparams, notes_map)
        for black_key in black_keys:
            black_key.on_raise(canvas)
        return piano