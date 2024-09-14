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

    def on_piano_resize(self, width, height):
        self.piano.resize(width, height)

    def begin(self):
        self.midi_file = self.load_midi("resource/audio/overworld.mid")
        self.root.geometry("1280x720")
        self.root.title("Midi Animation")
        creator = PianoCreator88()
        self.menu_bar = tk.Frame(self.root,bg='blue')
        self.menu_bar.place(relwidth=1, height=20)
        self.main_bar = tk.Frame(self.root,bg='yellow')
        self.main_bar.place(relwidth=1, y=20, relheight=1)
        self.piano_pane = tk.Frame(self.main_bar, bg='red')
        self.sidepane = tk.Frame(self.main_bar, bg='green')
        self.sidepane.place(relwidth=0.2, relheight=1)
        self.piano_pane.place(relx=0.2, rely=0.7, relwidth=0.8, relheight=0.3)
        initial_piano = PianoCreationParams(self.piano_pane, 1280, 720)
        self.piano = creator.create_piano(initial_piano)
        self.piano.canvas.grid(row=1,column=1, sticky='S')

        self.midi_notes_pane = tk.Frame(self.main_bar, bg='gray')
        self.midi_notes_pane.place(relx=0.2, relheight=0.7, relwidth=0.8)

        self.tracker = SizeTracker(self.piano_pane)
        self.tracker.register(self.on_piano_resize)
        self.tracker.bind_config()
        self.tracker.resize_to(1024, 204)
        self.root.mainloop()



if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()