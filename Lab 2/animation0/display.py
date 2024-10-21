import tkinter as tk

from actions import MidiAction, ActionFactory
from MusicPlayer import MusicPlayer
from global_controls import GlobalControls
from message_navigator import CachingMidiNavigator
from message_passing import MessagePassing, TickMessage, FinishTrackMessage, LengthMessage, ChannelColorMessage, \
    LoadFile, UpdateSideBar, ResetOnUnload, ControlMessage
from midis import MidiFile, SoundEvent, MidiMapper
from typing import List, Dict
from piano import Piano, PianoKey
from dynamic import DynamicMidiData, Defaults


class MidiService:
    @staticmethod
    def calculate_ticks(delta_time_ms: int, dynamic: DynamicMidiData) -> int:
        tempo_in_ms = dynamic.current_tempo / 1000
        return round((dynamic.ticks_per_beat * delta_time_ms) / tempo_in_ms)


class MidiNotesState:

    actions: List[MidiAction]
    dynamic: DynamicMidiData
    def __init__(self, dynamic: DynamicMidiData):
        self.dynamic = dynamic
        self.pointer_limit = 0
        self.create_pointer = 0
        self.slide_pointer = 0
        self.pressed_actions = []
        self.reset_time()
        self.actions = []
        self.navigator = CachingMidiNavigator(dynamic)

    def reset_time(self):
        self.create_pointer = 0
        self.slide_pointer = 0
        self.pressed_actions.clear()

    def on_load(self, actions : List[MidiAction]):
        self.reset_time()
        self.actions = list(actions)
        self.pointer_limit = len(actions)
        self.navigator.on_load_file(actions)

    def on_unload(self):
        self.reset_time()
        self.actions = []
        self.pointer_limit = 0
        self.navigator.on_unload_file()

    def set_time(self, time_to_set):
        self.dynamic.channel_programs = [0] * Defaults.channel_count()
        self.dynamic.current_tempo = Defaults.tempo()
        nav_state = self.navigator.set_time_to(time_to_set)
        self.slide_pointer = nav_state.pressed_pointer
        self.create_pointer = nav_state.created_pointer

        self.pressed_actions = list(nav_state.pressed_list)
        for event in nav_state.created_list:
            event.on_forced_register()
        for event in self.pressed_actions:
            event.on_forced_register()
            event.on_forced_press()


    def move_time_forward(self):
        updated_into_notes = self.dynamic.current_tick
        created = []
        while self.create_pointer < self.pointer_limit:
            event = self.actions[self.create_pointer]
            if updated_into_notes + self.dynamic.ticks_lookahead >= event.begin_when():
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
        for event in created:
            event.on_register()
        for event in pressed:
            event.on_press()
        for event in unpressed:
            event.on_release()



    def finished(self):
        return self.dynamic.current_tick > (self.dynamic.duration_ticks + self.dynamic.ticks_after)



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
        self.color = 'white'
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

    def clean(self):
        self.canvas.delete(self.shape)


class SlidingNotes:
    active_notes: List[SlidingNote]
    def __init__(self, dynamics: DynamicMidiData, piano: Piano):
        self.dynamics = dynamics
        self.piano = piano
        self.active_notes = []

    def include(self, sliding_note : SlidingNote):
        self.active_notes.append(sliding_note)

    def exclude(self, sliding_note : SlidingNote):
        sliding_note.clean()
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
        lookahead = self.dynamics.ticks_lookahead
        note_created = sliding_note.created_tick

        tick_note_fully_entered = sliding_note.end_tick - lookahead
        note_ticks_top = max(0, current_tick - tick_note_fully_entered)

        note_ticks_bottom = lookahead
        if sliding_note.press_tick > current_tick:
            note_ticks_bottom = (current_tick - note_created)
        height_ticks = note_ticks_bottom - note_ticks_top
        white_width = self.piano.dynamic_gfx.white_width
        black_width = self.piano.dynamic_gfx.black_width
        color = sliding_note.key_color
        key = sliding_note.key
        pixels_per_tick = self.dynamics.pixels_per_tick
        if color == "white":
            new_x = key.normalized_position * white_width
            sliding_note.move_to(new_x, note_ticks_top * pixels_per_tick)
            sliding_note.resize(white_width, height_ticks * pixels_per_tick)
        else:
            new_x = key.normalized_position * white_width
            sliding_note.move_to(new_x, note_ticks_top * pixels_per_tick)
            sliding_note.resize(black_width, height_ticks * pixels_per_tick)

    def when_resized(self):
        for note in self.active_notes:
            self.adjust_position(note)

    def clear(self):
        for note in self.active_notes:
            note.clean()
        self.active_notes.clear()

    def update_colors(self, channel):
        color = self.dynamics.channel_colors[channel]
        for note in self.active_notes:
            if note.channel_id == channel:
                note.set_channel_color(color)


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
        key = self.piano.key_id_of(event)
        sliding_note.key_color = key.color
        sliding_note.resize(20, 0)

        self.sliding_notes.adjust_position(sliding_note)
        channel = sliding_note.channel_id
        sliding_note.set_channel_color(self.dynamics.channel_colors[channel])
        self.notes_map[created_by] = sliding_note
        self.sliding_notes.include(sliding_note)

    def on_press(self, event : SoundEvent):
        self.piano.press(event)
    def on_release(self, event : SoundEvent):
        self.piano.release(event)
        sliding_note = self.notes_map.pop(event.identity)
        self.sliding_notes.exclude(sliding_note)
        sliding_note.remove()
    def update(self, ticks):
        self.sliding_notes.update_every_note(ticks)

    def when_resized(self):
        self.sliding_notes.when_resized()

    def clear(self):
        self.piano.release_all()
        self.sliding_notes.clear()
        self.notes_map.clear()

    def update_colors(self, channel):
        self.piano.update_colors()
        self.sliding_notes.update_colors(channel)


class MidiNotesDisplay:
    midi_notes_state : None | MidiNotesState
    def __init__(self,
                 root : tk.Frame,
                 piano : Piano,
                 dynamics: DynamicMidiData,
                 music_player : MusicPlayer,
                 global_control : GlobalControls,
                 message_passing : MessagePassing):
        self.root = root
        self.message_passing = message_passing
        self.dynamics = dynamics
        self.canvas = tk.Canvas(root, bg='gray')
        self.midi_notes_state = MidiNotesState(dynamics)
        self.music_player = music_player
        self.global_control = global_control
        self.note_animation = NoteAnimationHandler(self.canvas, piano, dynamics)
        self.actions_factory = ActionFactory(self.note_animation, dynamics, music_player)
        self.dynamics.current_tick = -self.dynamics.ticks_before
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.dynamics.pixels_per_tick = self.canvas.winfo_height() / self.dynamics.ticks_lookahead


    def load_notes(self, midi_file: MidiFile):
        action_list = self.actions_factory.create_all_actions(midi_file.events)
        self.midi_notes_state.on_load(action_list)
        self.global_control.is_loaded.set()
        self.global_control.is_playing.clear()
        self.global_control.is_finished.clear()
        self.message_passing.post_message(UpdateSideBar())
    def clear_notes(self):
        self.global_control.is_loaded.clear()
        self.global_control.is_playing.clear()
        self.global_control.is_finished.clear()
        self.midi_notes_state.on_unload()

    def on_resize(self, width, height):
        self.canvas.place(width=width, height=height)
        self.dynamics.pixels_per_tick =  self.canvas.winfo_height() / self.dynamics.ticks_lookahead
        self.note_animation.when_resized()

    def update(self, past_millis):
        self._read_messages()
        if not self.global_control.is_loaded.is_set():
            return
        if self.global_control.is_playing.is_set():
            ticks_passed = MidiService.calculate_ticks(past_millis, self.dynamics)
            self.midi_notes_state.move_time_forward()
            self.note_animation.update(ticks_passed)
            self.music_player.play_and_clear()
            if self.midi_notes_state.finished():
                self._finish()
            self.dynamics.current_tick = self.dynamics.current_tick + ticks_passed
    def _read_messages(self):
        unload_message = self.message_passing.pop_message("unload_file")
        if unload_message is not None:
            self.unload()
            self.message_passing.post_message(ResetOnUnload())
        load_file_message = self.message_passing.pop_message("load_file")
        if load_file_message is not None and isinstance(load_file_message, LoadFile):
            file = load_file_message.filename
            self.load_file(file)
        if not self.global_control.is_loaded.is_set():
            return

        pause_message = self.message_passing.pop_message("control")
        if pause_message is not None and isinstance(pause_message, ControlMessage):
            if pause_message.action == "pause":
                self.music_player.reset()
        tick_message = self.message_passing.pop_message("tick")
        if tick_message is not None and isinstance(tick_message, TickMessage):
            self.set_time(tick_message.tick)
        length_message = self.message_passing.pop_message("length")
        if length_message is not None and isinstance(length_message, LengthMessage):
            self._change_lookahead(length_message.length)
        color_message = self.message_passing.pop_message("color")
        if color_message is not None and isinstance(color_message, ChannelColorMessage):
            self._update_channel_color(color_message.updated_channel)

    def _change_lookahead(self, measure):
        self.dynamics.ticks_lookahead = measure * 400
        self.dynamics.pixels_per_tick = self.canvas.winfo_height() / self.dynamics.ticks_lookahead
        self.note_animation.clear()
        self.midi_notes_state.set_time(self.dynamics.current_tick)

    def _update_channel_color(self, channel):
        self.note_animation.update_colors(channel)
    def _finish(self):
        self.global_control.is_finished.set()
        self.stop()
        self.message_passing.post_message(FinishTrackMessage())

    def play(self):
        if not self.global_control.is_loaded.is_set():
            return
        if self.global_control.is_finished.is_set():
            return
        self.global_control.is_playing.set()

    def set_time(self, new_tick):
        self.music_player.reset()
        self.note_animation.clear()
        self.dynamics.current_tick = new_tick
        self.midi_notes_state.set_time(new_tick)
    def load_file(self, file_to_load):
        self.unload()
        mapped_file = MidiMapper.map_to_midi_file(file_to_load)
        self.apply_metadata(mapped_file)
        self.load_notes(mapped_file)
        self.dynamics.current_tick = -Defaults.time_before()
        self.set_time(Defaults.time_before())
    def unload(self):
        self.clear_notes()
        self.music_player.reset()
        self.note_animation.clear()
        self.dynamics.current_tick = 0
        self.dynamics.channel_programs = [0] * Defaults.channel_count()
        self.dynamics.channel_colors = list(self.dynamics.default_colors)

    def apply_metadata(self, mapped_file):
        self.dynamics.ticks_per_beat = mapped_file.metadata.ticks_per_beat
        self.dynamics.duration_ticks = mapped_file.metadata.duration_ticks

    def stop(self):
        if not self.global_control.is_loaded.is_set():
            return
        self.global_control.is_playing.clear()
