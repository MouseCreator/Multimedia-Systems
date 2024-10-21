import tkinter as tk

from MusicPlayer import MusicPlayer
from display import MidiNotesDisplay
from dynamic import DynamicMidiData
from engine import Engine
from global_controls import GlobalControls
from menu_bar import MenuBar
from message_passing import MessagePassing
from piano import PianoCreator88, PianoCreationParams, Piano
from defines import *
from side_menu import SideMenu
from size import SizeTracker

class MidiPlayer:

    piano: Piano | None
    notes_display: MidiNotesDisplay | None
    size_tracker: SizeTracker | None
    engine: Engine | None
    music_player: MusicPlayer | None
    global_controls : GlobalControls | None
    side_menu_control : SideMenu | None
    menu_control: MenuBar | None
    def __init__(self):
        self.root = tk.Tk()
        self.dynamics = DynamicMidiData()
        self.message_passing = MessagePassing()
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
        self.menu_control = None

    def on_resize(self, width, height):
        self.piano.resize(width-DEFINES.ABS_SIDEBAR_WIDTH, height*DEFINES.REL_PIANO_HEIGHT)
        self.notes_display.on_resize(width-DEFINES.ABS_SIDEBAR_WIDTH, height*DEFINES.REL_MIDI_PLAYER_HEIGHT)

    def setup_meta(self):
        self.music_player = MusicPlayer()
        self.music_player.start()

    def setup_layout(self):

        self.root.geometry(f"{DEFINES.DEFAULT_WINDOW_WIDTH}x{DEFINES.DEFAULT_WINDOW_HEIGHT}")
        self.root.title("Midi Animation")
        self.root.minsize(DEFINES.MIN_WINDOW_WIDTH, DEFINES.MIN_WINDOW_HEIGHT)
        creator = PianoCreator88()
        self.menu_bar = tk.Frame(self.root, bg='white')
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


        self.menu_control = MenuBar(self.dynamics, self.message_passing, self.root)

        self.side_menu_control = SideMenu(self.side_pane, self.global_controls, self.dynamics, self.message_passing)
        self.size_tracker = SizeTracker(self.root)
        self.size_tracker.register(self.on_resize)
        self.size_tracker.bind_config()
        self.size_tracker.resize_to(DEFINES.DEFAULT_WINDOW_WIDTH, DEFINES.DEFAULT_WINDOW_HEIGHT)
        self.engine.register(self.menu_control.update)
        self.engine.register(self.side_menu_control.update)
        self.engine.register(self.notes_display.update)
        self.engine.start()
    def main_loop(self):
        self.root.mainloop()

    def begin(self):
        self.setup_meta()
        self.setup_layout()
        self.main_loop()




if __name__ == '__main__':
    player = MidiPlayer()
    player.begin()