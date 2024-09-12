import mido as md
import tkinter as tk


def load_midi(file_path):
    midi = md.MidiFile(file_path)
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

load_midi("resource/audio/overworld.mid")