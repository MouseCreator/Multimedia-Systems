import mido
import tkinter as tk

from MusicPlayer import MusicPlayer
from display import MidiNotesDisplay
from dynamic import DynamicMidiData
from engine import Engine
from global_controls import GlobalControls
from message_passing import MessagePassing
from midis import MidiMapper
from piano import PianoCreator88, PianoCreationParams, Piano
from defines import *
from side_menu import SideMenu
from size import SizeTracker

FILE_TO_LOAD = "resource/audio/polkka.mid"
class MidiPlayer:

    piano: Piano | None
    notes_display: MidiNotesDisplay | None
    size_tracker: SizeTracker | None
    engine: Engine | None
    music_player: MusicPlayer | None
    global_controls : GlobalControls | None
    side_menu_control : SideMenu | None
    def __init__(self):
        self.root = tk.Tk()
        self.dynamics = DynamicMidiData()
        self.message_passing = MessagePassing()
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
        self.music_player = None
        self.global_controls = None
        self.side_menu_control = None

    def on_resize(self, width, height):
        self.piano.resize(width-DEFINES.ABS_SIDEBAR_WIDTH, height*DEFINES.REL_PIANO_HEIGHT)
        self.notes_display.on_resize(width-DEFINES.ABS_SIDEBAR_WIDTH, height*DEFINES.REL_MIDI_PLAYER_HEIGHT)

    def setup_meta(self):
        self.music_player = MusicPlayer()
        self.music_player.start()
        self.midi_file = self.load_midi(FILE_TO_LOAD)

    def setup_layout(self):

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
        self.side_pane.place(width=DEFINES.ABS_SIDEBAR_WIDTH, relheight=1)
        self.piano_pane.place(x=DEFINES.ABS_SIDEBAR_WIDTH,
                              rely=DEFINES.REL_MIDI_PLAYER_HEIGHT,
                              relwidth=1,
                              relheight=DEFINES.REL_PIANO_HEIGHT)
        initial_piano = PianoCreationParams(self.piano_pane, DEFINES.DEFAULT_PIANO_WIDTH, DEFINES.DEFAULT_PIANO_HEIGHT)
        self.piano = creator.create_piano(self.dynamics, initial_piano)
        self.engine = Engine(self.root)
        self.midi_notes_pane = tk.Frame(self.main_bar, bg='gray')
        self.midi_notes_pane.place(x=DEFINES.ABS_SIDEBAR_WIDTH,
                                   relheight=DEFINES.REL_MIDI_PLAYER_HEIGHT,
                                   relwidth=1)
        self.global_controls = GlobalControls()
        self.notes_display = MidiNotesDisplay(
            self.midi_notes_pane,
            self.piano,
            self.dynamics,
            self.music_player,
            self.global_controls,
            self.message_passing)
        mapped_file = MidiMapper.map_to_midi_file(FILE_TO_LOAD)
        self.apply_metadata(mapped_file)

        self.side_menu_control = SideMenu(self.side_pane, self.global_controls, self.dynamics, self.message_passing)

        self.size_tracker = SizeTracker(self.root)
        self.size_tracker.register(self.on_resize)
        self.size_tracker.bind_config()
        self.size_tracker.resize_to(DEFINES.DEFAULT_WINDOW_WIDTH, DEFINES.DEFAULT_WINDOW_HEIGHT)

        self.notes_display.load_notes(mapped_file)
        self.notes_display.set_time(8000)
        self.notes_display.play()
        self.engine.register(self.side_menu_control.update)
        self.engine.register(self.notes_display.update)
        self.engine.register(self._clean_message_passing)
        self.engine.start()
    def _clean_message_passing(self, millis):
        self.message_passing.ignore_rest()
    def main_loop(self):
        self.root.mainloop()

    def begin(self):
        self.setup_meta()
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

    def apply_metadata(self, mapped_file):
        self.dynamics.ticks_per_beat = mapped_file.metadata.ticks_per_beat
        self.dynamics.duration_ticks = mapped_file.metadata.duration_ticks


if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()