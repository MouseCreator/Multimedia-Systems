import tkinter as tk

from midis import MidiFile, MidiEvent, SoundEvent, ProgramChangeEvent, TempoEvent
import threading
from typing import List, Dict
from abc import ABC, abstractmethod
from piano import Piano, PianoKey
from dynamic import DynamicMidiData

class MidiService:
    @staticmethod
    def calculate_ticks(delta_time_ms: int, dynamic: DynamicMidiData) -> int:
        tempo_in_ms = dynamic.current_tempo / 1000
        return round((dynamic.ticks_per_beat * delta_time_ms) / tempo_in_ms)

class MidiAction(ABC):
    @abstractmethod
    def begin_when(self):
        pass
    @abstractmethod
    def end_when(self):
        pass

    def on_register(self):
        pass

    def on_press(self):
        pass

    def on_release(self):
        pass

class SoundAction(MidiAction):

    def __init__(self, sound_event: SoundEvent, animation_handler):
        self.sound_event = sound_event
        self.animation_handler = animation_handler
    def on_register(self):
        self.animation_handler.on_register(self.sound_event)
    def on_press(self):
        self.animation_handler.on_press(self.sound_event)
    def on_release(self):
        self.animation_handler.on_release(self.sound_event)
    def begin_when(self):
        return self.sound_event.begin_when
    def end_when(self):
        return self.sound_event.end_when

class TempoAction(MidiAction):

    def begin_when(self):
        return self.tempo_event.begin_when

    def end_when(self):
        return self.tempo_event.begin_when

    def __init__(self, tempo_event: TempoEvent, dynamics: DynamicMidiData):
        self.tempo_event = tempo_event
        self.dynamics = dynamics


    def on_register(self):
        self.dynamics.current_tempo = self.tempo_event.tempo

class ProgramAction(MidiAction):
    def begin_when(self):
        return self.program_event.begin_when

    def end_when(self):
        return self.program_event.begin_when

    def __init__(self, event: ProgramChangeEvent, dynamics: DynamicMidiData):
        self.program_event = event
        self.dynamics = dynamics

    def on_press(self):
        channel = self.program_event.channel
        program = self.program_event.program
        self.dynamics.channel_programs[channel] = program
class ActionFactory:
    def __init__(self, animation_handler, dynamics: DynamicMidiData):
        self.animation_handler = animation_handler
        self.dynamics = dynamics
    def create_action(self, event: MidiEvent) -> MidiAction:
        if isinstance(event, SoundEvent):
            return self._create_sound_action(event)
        elif isinstance(event, ProgramChangeEvent):
            return self._create_program_action(event)
        elif isinstance(event, TempoEvent):
            return self._create_tempo_action(event)
        else:
            raise Exception(f"Unknown event to convert: {event}")

    def _create_sound_action(self, sound_event: SoundEvent) -> SoundAction:
        return SoundAction(sound_event, self.animation_handler)

    def _create_program_action(self, program_change_event : ProgramChangeEvent) -> ProgramAction:
        return ProgramAction(program_change_event, self.dynamics)

    def _create_tempo_action(self, event: TempoEvent) -> TempoAction:
        return TempoAction(event, self.dynamics)

    def create_all_actions(self, events : List[MidiEvent]) -> List[MidiAction]:
        actions = []
        for event in events:
            action = self.create_action(event)
            actions.append(action)
        return actions

class MidiNotesState:

    actions: List[MidiAction]

    def __init__(self, actions: List[MidiAction], duration: int, ticks_before=0, ticks_after=1000):
        self.actions = actions
        self.pointer_limit = len(actions)
        self.lookahead_ticks = 1500
        self.ticks_before = ticks_before
        self.ticks_after = ticks_after
        self.duration_ticks = duration
        self.current_tick = 0
        self.tick_into_notes = 0
        self.full_length = ticks_before + duration + ticks_after
        self.create_pointer = 0
        self.slide_pointer = 0
        self.press_pointer = 0
        self.pressed_actions = []
        self.reset_time()

    def reset_time(self):
        self.current_tick = 0
        self.tick_into_notes = self.current_tick - self.ticks_before
        self.create_pointer = 0
        self.slide_pointer = 0
        self.press_pointer = 0
        self.pressed_actions.clear()


    def move_time_forward(self, by_ticks: int):
        updated_tick = self.current_tick + by_ticks
        updated_into_notes = self.tick_into_notes + by_ticks
        created = []
        while self.create_pointer < self.pointer_limit:
            event = self.actions[self.create_pointer]
            if updated_into_notes + self.lookahead_ticks >= event.begin_when():
                created.append(event)
                self.create_pointer += 1
            else:
                break
        pressed = []
        while self.slide_pointer < self.pointer_limit:
            event = self.actions[self.slide_pointer]
            if updated_into_notes >= event.begin_when():
                pressed.append(event)
                self.slide_pointer += 1
                self.pressed_actions.append(event)
            else:
                break

        unpressed = []
        for event in self.pressed_actions:
            if updated_into_notes >= event.end_when():
                unpressed.append(event)
        for event in unpressed:
            self.pressed_actions.remove(event)
        self.current_tick = updated_tick
        self.tick_into_notes = updated_into_notes
        for event in created:
            event.on_register()
        for event in pressed:
            event.on_press()
        for event in unpressed:
            event.on_release()

    def finished(self):
        return self.current_tick > self.full_length



class SlidingNote:
    def __init__(self,
                 created_by_id: int,
                 key: PianoKey,
                 channel_id: int,
                 created_tick: int,
                 press_tick: int,
                 end_tick: int,
                 canvas: tk.Canvas):
        self.created_by_id = created_by_id
        self.press_tick = press_tick
        self.created_tick = created_tick
        self.canvas = canvas
        self.key = key
        self.channel_id = channel_id
        self.end_tick = end_tick
        self.key_color = 'white'
        self.shape = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.key_color)
        self.pos_x = 0
        self.pos_y = 0
        self.width = 0
        self.height = 0
        self.building = True

    def move_by(self, x, y):
        self.pos_x += x
        self.pos_y += y
        self.canvas.move(self.shape, x, y)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.canvas.coords(self.shape, self.pos_x, self.pos_y, self.pos_x+self.width, self.pos_y+self.height)

    def set_channel_color(self, color):
        self.color = color
        self.canvas.itemconfig(self.shape, fill=color)

    def remove(self):
        self.canvas.delete(self.shape)

    def stretch_by(self, add_width, add_height):
        self.width = self.width + add_width
        self.height = self.height + add_height
        self.canvas.coords(self.shape, self.pos_x, self.pos_y, self.pos_x+self.width, self.pos_y+self.height)

    def move_to(self, new_x, new_y):
        by_x = new_x - self.pos_x
        by_y = new_y - self.pos_y
        self.pos_x = new_x
        self.pos_y = new_y
        self.canvas.move(self.shape, by_x, by_y)


class SlidingNotes:
    active_notes: List[SlidingNote]
    def __init__(self, dynamics: DynamicMidiData, piano: Piano):
        self.dynamics = dynamics
        self.piano = piano
        self.active_notes = []

    def include(self, sliding_note : SlidingNote):
        self.active_notes.append(sliding_note)

    def exclude(self, sliding_note : SlidingNote):
        self.active_notes.remove(sliding_note)

    def update_every_note(self, ticks_passed):
        current = self.dynamics.current_tick
        for active_note in self.active_notes:
            self._move_sliding_note(active_note, current, ticks_passed)

    def _move_sliding_note(self, active_note: SlidingNote, current : int, ticks_passed : int):
        ending = active_note.end_tick
        move_value = 0
        visible_lookahead = current + self.dynamics.ticks_lookahead
        visible_lookahead_next = visible_lookahead + ticks_passed
        next_tick = current + ticks_passed
        stretch_value = 0
        camera_moved_by = ticks_passed * self.dynamics.pixels_per_tick
        if ending > visible_lookahead:
             stretch_value = camera_moved_by
        elif visible_lookahead_next > ending > visible_lookahead :
            ticks_build = ending - visible_lookahead
            ticks_move = next_tick - ending
            move_value = ticks_move * self.dynamics.pixels_per_tick
            stretch_value = ticks_build * self.dynamics.pixels_per_tick
        elif visible_lookahead_next > ending:
             move_value = camera_moved_by
        if stretch_value > 0:
            active_note.stretch_by(0, stretch_value)
        if move_value > 0:
            active_note.move_by(0, move_value)

    def adjust_position(self, sliding_note: SlidingNote):
        current_tick = self.dynamics.current_tick
        note_created = sliding_note.created_tick
        note_alive = current_tick - note_created
        note_full = sliding_note.end_tick - sliding_note.press_tick
        size_def = min(note_alive, note_full)
        white_width = self.piano.dynamic_gfx.white_width
        black_width = self.piano.dynamic_gfx.black_width
        color = sliding_note.key_color
        key = sliding_note.key
        pixels_per_tick = self.dynamics.pixels_per_tick
        if color == "white":
            new_x = key.normalized_position * white_width
            sliding_note.move_to(new_x, note_alive * pixels_per_tick)
            sliding_note.resize(white_width, size_def * pixels_per_tick)
        else:
            new_x = key.normalized_position * white_width
            sliding_note.move_to(new_x, note_alive * pixels_per_tick)
            sliding_note.resize(black_width, size_def * pixels_per_tick)

    def when_resized(self):
        for note in self.active_notes:
            self.adjust_position(note)



class NoteAnimationHandler:
    notes_map: Dict[int, SlidingNote]
    def __init__(self, canvas : tk.Canvas, piano: Piano, dynamics:DynamicMidiData):
        self.piano = piano
        self.dynamics = dynamics
        self.sliding_notes = SlidingNotes(dynamics, piano)
        self.notes_map = {}
        self.canvas = canvas
    def on_register(self, event : SoundEvent):
        created_by = event.identity
        key_id = self.piano.key_id_of(event)
        sliding_note = SlidingNote(
            created_by_id = created_by,
            key = key_id,
            channel_id=event.channel,
            created_tick=event.begin_when - self.dynamics.ticks_lookahead,
            press_tick=event.begin_when,
            end_tick=event.end_when,
            canvas=self.canvas
        )
        sliding_note.resize(20, 0)

        self.sliding_notes.adjust_position(sliding_note)
        channel = sliding_note.channel_id
        sliding_note.set_channel_color(self.dynamics.channel_colors[channel])
        self.notes_map[created_by] = sliding_note
        self.sliding_notes.include(sliding_note)
        print(f"Register {event.identity}")

    def on_press(self, event : SoundEvent):
        self.piano.press(event)
        print(f"Press {event.identity}")
    def on_release(self, event : SoundEvent):
        print(f"Release {event.identity}")
        self.piano.release(event)
        sliding_note = self.notes_map.pop(event.identity)
        self.sliding_notes.exclude(sliding_note)
        sliding_note.remove()
    def update(self, ticks):
        self.sliding_notes.update_every_note(ticks)

    def when_resized(self):
        self.sliding_notes.when_resized()


class MidiNotesDisplay:
    # TODO: FOR AUDIO OUTPUT ADD ASSOCIATED EVENTS (origins)
    def __init__(self, root : tk.Frame, piano : Piano, dynamics: DynamicMidiData):
        self.root = root
        self.dynamics = dynamics
        self.canvas = tk.Canvas(root, bg='gray')
        self.mini_notes_state = None
        self.is_loaded = threading.Event()
        self.is_loaded.clear()
        self.is_playing = threading.Event()
        self.is_playing.clear()
        self.is_finished = threading.Event()
        self.is_finished.clear()

        self.note_animation = NoteAnimationHandler(self.canvas, piano, dynamics)
        self.actions_factory = ActionFactory(self.note_animation, dynamics)
        self.dynamics.current_tick = 0
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.dynamics.pixels_per_tick = self.canvas.winfo_height() / self.dynamics.ticks_lookahead


    def load_notes(self, midi_file: MidiFile):
        duration_ticks = midi_file.metadata.duration_ticks
        action_list = self.actions_factory.create_all_actions(midi_file.events)
        self.mini_notes_state = MidiNotesState(action_list, duration_ticks)
        self.is_loaded.set()
        self.is_playing.clear()
        self.is_finished.clear()

    def clear_notes(self):
        self.is_loaded.clear()
        self.is_playing.clear()
        self.is_finished.clear()
        self.mini_notes_state = None

    def on_resize(self, width, height):
        self.canvas.place(width=width, height=height)
        self.dynamics.pixels_per_tick =  self.canvas.winfo_height() / self.dynamics.ticks_lookahead
        self.note_animation.when_resized()

    def update(self, past_millis):
        if not self.is_loaded.is_set():
            print("NOT LOADED")
            return
        if self.is_playing.is_set():
            ticks_passed = MidiService.calculate_ticks(past_millis, self.dynamics)
            self.mini_notes_state.move_time_forward(ticks_passed)
            self.note_animation.update(ticks_passed)
            if self.mini_notes_state.finished():
                print("FINISH")
                self._finish()
            self.dynamics.current_tick = self.dynamics.current_tick + ticks_passed

    def _finish(self):
        self.is_finished.set()
        self.stop()

    def play(self):
        if not self.is_loaded.is_set():
            return
        if self.is_finished.is_set():
            return
        self.is_playing.set()

    def set_time(self, time_millis):
        if not self.is_loaded.is_set():
            return
        if self.mini_notes_state.finished():
            self.is_finished.set()
        else:
            self.is_finished.clear()

    def stop(self):
        if not self.is_loaded.is_set():
            return
        self.is_playing.clear()
