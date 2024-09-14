import mido
import tkinter as tk
from piano import PianoCreator88, PianoCreationParams
from defines import *
from size import SizeTracker


class MidiPlayer:
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


    def __init__(self):
        self.root = tk.Tk()
        self.midi_file = ""
        self.piano = None
        self.menu_bar = None
        self.side_pane = None
        self.piano_pane = None
        self.main_bar = None
        self.midi_notes_pane = None
        self.size_tracker = None

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

        self.midi_notes_pane = tk.Frame(self.main_bar, bg='gray')
        self.midi_notes_pane.place(relx=DEFINES.REL_SIDEBAR_WIDTH,
                                   relheight=DEFINES.REL_MIDI_PLAYER_HEIGHT,
                                   relwidth=DEFINES.REL_PIANO_WIDTH)

        self.size_tracker = SizeTracker(self.piano_pane)
        self.size_tracker.register(self.on_piano_resize)
        self.size_tracker.bind_config()
        self.size_tracker.resize_to(DEFINES.DEFAULT_PIANO_WIDTH, DEFINES.DEFAULT_PIANO_HEIGHT)

    def main_loop(self):
        self.root.mainloop()

    def begin(self):
        self.setup_layout()
        self.main_loop()



if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()