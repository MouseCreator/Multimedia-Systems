import mido
import tkinter as tk
from piano import PianoCreator88

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

    def create_canvas(self):
        self.root.geometry("1280x720")
        self.root.title("Midi Animation")

    def create_piano_keys(self):
        pass


    def __init__(self):
        self.root = tk.Tk()
        self.midi_file = ""
    def begin(self):
        self.midi_file = self.load_midi("resource/audio/overworld.mid")
        creator = PianoCreator88()
        piano = creator.create_piano(self.root)
        self.root.mainloop()



if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()