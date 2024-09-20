import tkinter as tk

from midis import MidiFile, MidiEvent
import threading
from typing import List, Dict

from piano import Piano

class NoteGraphic:
    def __init__(self, root : tk.Canvas, duration_millis, color = 'white'):
        self.root = root
        self.pos_x = 0
        self.pos_y = 0
        self.width = 0
        self.height = 0
        self.color = color
        self.duration_millis = duration_millis
        self.graphic = self.root.create_rectangle(0, 0, 0, 0, fill=color)
    def move_by(self, x, y):
        self.pos_x += x
        self.pos_y += y
        self.root.move(self.graphic, x, y)
    def resize(self, width, height):
        self.width = width
        self.height = height
        self.root.coords(self.graphic, self.pos_x, self.pos_y, self.pos_x+self.width, self.pos_y+self.height)
    def set_channel_color(self, color):
        self.color = color
        self.root.itemconfig(self.graphic, fill=color)
    def remove(self):
        self.root.delete(self.graphic)

class DisplayableNote:
    def __init__(self, note: MidiEvent, graphic: NoteGraphic):
        self.note = note
        self.graphic = graphic


class DisplayEvent:
    def __init__(self, midi_event: MidiEvent, e_type: str):
        self.midi_event = midi_event
        self.e_type = e_type

class MidiNotesState:

    notes: List[MidiEvent]

    def __init__(self, notes: List[MidiEvent], duration: int, millis_before=1000, millis_after=1000):
        self.notes = notes
        self.lookahead_millis = 1500
        self.millis_before = millis_before
        self.millis_after = millis_after
        self.duration = duration
        self.time = 0
        self.time_into_notes = 0
        self.full_length = duration + millis_before + millis_after
        self.create_queue = []
        self.slide_queue = []
        self.pressed_queue = []
        self.set_time_to(0)

    def set_time_to(self, time_millis):
        self.time = time_millis
        self.time_into_notes = self.time - self.millis_before
        self.create_queue.clear()
        self.slide_queue.clear()
        self.slide_queue.clear()
        after_lookahead = self.time + self.lookahead_millis
        align_events = []
        for note in self.notes:
            if note.end_when <= self.time_into_notes:
                # note has already played
                continue
            if note.begin_when <= self.time_into_notes:
                # note is playing
                self.pressed_queue.append(note)
                align_events.append(DisplayEvent(note, "align"))
            elif note.begin_when <= after_lookahead:
                # note is sliding
                self.slide_queue.append(note)
                align_events.append(DisplayEvent(note, "align"))
            else:
                # note has not been created yet
                self.create_queue.append(note)
        return align_events
    def move_time_forward(self, by_millis: int) -> List[DisplayEvent]:
        updated_time = self.time + by_millis
        updated_into_notes = self.time_into_notes + by_millis
        print(self.time_into_notes)
        created = []
        while len(self.create_queue) > 0:
            event = self.create_queue[0]
            if updated_into_notes + self.lookahead_millis >= event.begin_when:
                created.append(event)
                self.create_queue.pop(0)
            else:
                break
        pressed = []
        while len(self.slide_queue) > 0:
            event = self.slide_queue[0]
            if updated_into_notes >= event.begin_when:
                pressed.append(event)
                self.slide_queue.pop(0)
            else:
                break
        for event in created:
            self.slide_queue.append(event)
        unpressed = []
        for event in self.pressed_queue:
            if updated_into_notes >= event.end_when:
                unpressed.append(event)
        for event in unpressed:
            self.pressed_queue.remove(event)
        self.time = updated_time
        self.time_into_notes = updated_into_notes
        display_events = []
        for event in created:
            display_events.append(DisplayEvent(event, "register"))
        for event in pressed:
            display_events.append(DisplayEvent(event, "press"))
        for event in unpressed:
            display_events.append(DisplayEvent(event, "destroy"))
        return display_events

    def finished(self):
        return self.time > self.full_length


class MidiNotesEventConsumer:
    note_displays: Dict[int, DisplayableNote]
    def __init__(self, context: tk.Canvas, piano: Piano, width, height):
        self.context = context
        self.piano = piano
        self.note_displays = {} # int id : note_display
        self.width = width
        self.height = height
        self.scroll_speed = 5
        self.time_on_screen = self.height / self.scroll_speed
        self.pixels_per_millisecond = self.height / self.time_on_screen

    def update_geometry(self, width, height):
        self.width = width
        self.height = height
        self.pixels_per_millisecond = self.height / self.time_on_screen

    def set_speed(self, speed):
        self.scroll_speed = speed
        self.time_on_screen = self.height / self.scroll_speed

    def align_key(self, displayable: DisplayableNote, duration: int):
        white_only = self.piano.pparams.keys_white
        white_width = self.piano.dynamic_gfx.white_width
        black_width = self.piano.dynamic_gfx.black_width
        key = self.piano.key_id_of(displayable.note)
        color = key.color

        height = self.pixels_per_millisecond * duration

        if color == "white":
            new_x = key.normalized_position * white_width / 2
            displayable.graphic.move_by(new_x, -height)
            displayable.graphic.resize(white_width, height)
        else:
            new_x = key.normalized_position * white_width / 2
            displayable.graphic.move_by(new_x, -height)
            displayable.graphic.resize(black_width, height)

    def process_events(self, past_millis, display_events: List[DisplayEvent]):
        for display in self.note_displays.values():
            gr = display.graphic
            gr.move_by(0, past_millis * self.pixels_per_millisecond)
        for event in display_events:
            if event.e_type == "register":
                #append display event
                print("register")
                if event.midi_event.event_type()=="sound":
                    self.create_graphics_for(event)
            elif event.e_type == "press":
                print("pressing")
                # press piano key
                if event.midi_event.event_type()=="sound":
                    self.piano.press(event.midi_event)
                elif event.midi_event.event_type()=="program":
                    print("Change program info")
            elif event.e_type == "destroy":
                # out of bounds, no longer track
                self.piano.release(event.midi_event)
                graphic = self.note_displays.pop(event.midi_event.identity, __default=None)
                if graphic:
                    graphic.graphic.remove()
            elif event.e_type == "align":
                # unexpected
                raise Exception("Unexpected align event while playing midi file")
            else:
                raise Exception("Unknown event type")

    def create_graphics_for(self, event):
        duration = event.midi_event.end_when - event.midi_event.begin_when
        graphic = NoteGraphic(self.context, duration, color='red')
        displayable = DisplayableNote(event.midi_event, graphic)
        self.align_key(displayable, duration)
        self.note_displays[event.midi_event.identity] = displayable

    def recreate(self, new_time, display_events: List[DisplayEvent]):
        pass

class MidiNotesDisplay:

    def __init__(self, root : tk.Frame, piano : Piano):
        self.root = root
        self.canvas = tk.Canvas(root, bg='gray')
        self.mini_notes_state = None
        self.event_consumer = MidiNotesEventConsumer(self.canvas, piano, root.winfo_width(), root.winfo_height())
        self.is_loaded = threading.Event()
        self.is_loaded.clear()
        self.is_playing = threading.Event()
        self.is_playing.clear()
        self.is_finished = threading.Event()
        self.is_finished.clear()
        self.canvas.pack(fill=tk.BOTH, expand=True)


    def load_notes(self, midi_file: MidiFile):
        duration = midi_file.duration
        self.mini_notes_state = MidiNotesState(midi_file.events, duration)
        self.is_loaded.set()
        self.is_playing.clear()
        self.is_finished.clear()

    def clear_notes(self):
        self.is_loaded.clear()
        self.is_playing.clear()
        self.is_finished.clear()
        self.mini_notes_state = None

    def update(self, past_millis):

        if not self.is_loaded.is_set():
            print("NOT LOADED")
            return
        if self.is_playing.is_set():
            display_events = self.mini_notes_state.move_time_forward(past_millis)
            self.event_consumer.process_events(past_millis, display_events)
            if self.mini_notes_state.finished():
                print("FINISH")
                self._finish()

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
        update_events = self.mini_notes_state.set_time_to(time_millis)
        self.event_consumer.recreate(time_millis, update_events)
        if self.mini_notes_state.finished():
            self.is_finished.set()
        else:
            self.is_finished.clear()

    def stop(self):
        if not self.is_loaded.is_set():
            return
        self.is_playing.clear()

