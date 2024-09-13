import mido
import tkinter as tk
from piano import PianoCreator88, PianoCreationParams

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
    def begin(self):
        self.midi_file = self.load_midi("resource/audio/overworld.mid")
        self.root.geometry("1540x720")
        self.root.title("Midi Animation")
        creator = PianoCreator88()
        initial_piano = PianoCreationParams(self.root, 1280, 200)
        self.piano = creator.create_piano(initial_piano)
        self.root.mainloop()



if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()