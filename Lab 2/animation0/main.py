import mido
import tkinter as tk

from display import MidiNotesDisplay
from engine import Engine
from midis import MidiMapper
from piano import PianoCreator88, PianoCreationParams, Piano
from defines import *
from size import SizeTracker


class MidiPlayer:

    piano: Piano | None
    notes_display: MidiNotesDisplay | None
    size_tracker: SizeTracker | None
    engine: Engine | None

    def __init__(self):
        self.root = tk.Tk()
        self.midi_file = None
        self.piano = None
        self.menu_bar = None
        self.side_pane = None
        self.engine = None
        self.piano_pane = None
        self.main_bar = None
        self.midi_notes_pane = None
        self.size_tracker = None
        self.notes_display = None

    def on_piano_resize(self, width, height):
        self.piano.resize(width, height)
    def setup_layout(self):
        self.midi_file = self.load_midi("resource/audio/overworld.mid")
        self.root.geometry(f"{DEFINES.DEFAULT_WINDOW_WIDTH}x{DEFINES.DEFAULT_WINDOW_HEIGHT}")
        self.root.title("Midi Animation")
        self.root.minsize(DEFINES.MIN_WINDOW_WIDTH, DEFINES.MIN_WINDOW_HEIGHT)
        creator = PianoCreator88()
        self.menu_bar = tk.Frame(self.root, bg='blue')
        self.menu_bar.place(relwidth=1, height=DEFINES.MENU_HEIGHT_PX)
        self.main_bar = tk.Frame(self.root, bg='yellow')
        self.main_bar.place(relwidth=1, y=DEFINES.MENU_HEIGHT_PX, relheight=1)
        self.piano_pane = tk.Frame(self.main_bar, bg='red')
        self.side_pane = tk.Frame(self.main_bar, bg='green')
        self.side_pane.place(relwidth=DEFINES.REL_SIDEBAR_WIDTH, relheight=1)
        self.piano_pane.place(relx=DEFINES.REL_SIDEBAR_WIDTH,
                              rely=DEFINES.REL_MIDI_PLAYER_HEIGHT,
                              relwidth=DEFINES.REL_PIANO_WIDTH,
                              relheight=DEFINES.REL_PIANO_HEIGHT)
        initial_piano = PianoCreationParams(self.piano_pane, DEFINES.DEFAULT_PIANO_WIDTH, DEFINES.DEFAULT_PIANO_HEIGHT)
        self.piano = creator.create_piano(initial_piano)

        self.engine = Engine(self.root)
        self.midi_notes_pane = tk.Frame(self.main_bar, bg='gray')
        self.midi_notes_pane.place(relx=DEFINES.REL_SIDEBAR_WIDTH,
                                   relheight=DEFINES.REL_MIDI_PLAYER_HEIGHT,
                                   relwidth=DEFINES.REL_PIANO_WIDTH)

        self.notes_display = MidiNotesDisplay(self.midi_notes_pane, self.piano)
        self.notes_display.load_notes(MidiMapper.map_to_midi_file("resource/audio/overworld.mid"))
        self.notes_display.play()
        self.engine.register(self.notes_display.update)
        self.size_tracker = SizeTracker(self.piano_pane)
        self.size_tracker.register(self.on_piano_resize)
        self.size_tracker.bind_config()
        self.size_tracker.resize_to(DEFINES.DEFAULT_PIANO_WIDTH, DEFINES.DEFAULT_PIANO_HEIGHT)
        self.engine.start()

    def main_loop(self):
        self.root.mainloop()

    def begin(self):
        self.setup_layout()
        self.main_loop()

    def load_midi(self, file_path):
        midi = mido.MidiFile(file_path)
        print(f"Number of tracks: {len(midi.tracks)}")
        total_notes = 0
        for i, track in enumerate(midi.tracks):
            note_count = 0
            for msg in track:
                if msg.type == 'note_on' or msg.type == 'note_off':
                    note_count += 1
            total_notes += note_count
            print(f"Track {i+1}: {note_count} notes")

        print(f"Total notes in the MIDI file: {total_notes}")
        return midi


if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()