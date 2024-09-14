
class Defines:
    def __init__(self):
        self.DEFAULT_WINDOW_WIDTH=1280
        self.DEFAULT_WINDOW_HEIGHT=720
        self.MENU_HEIGHT_PX=20
        self.REL_SIDEBAR_WIDTH = 0.2
        self.REL_PIANO_HEIGHT = 0.25
        self.MIN_WINDOW_WIDTH = 640
        self.MIN_WINDOW_HEIGHT = 480
        self.REL_PIANO_WIDTH = 1 - self.REL_SIDEBAR_WIDTH
        self.REL_MIDI_PLAYER_HEIGHT = 1- self.REL_PIANO_HEIGHT
        self.DEFAULT_PIANO_WIDTH = self.DEFAULT_WINDOW_WIDTH * self.REL_PIANO_WIDTH
        self.DEFAULT_PIANO_HEIGHT = (self.DEFAULT_WINDOW_HEIGHT - self.MENU_HEIGHT_PX) * self.REL_PIANO_HEIGHT

DEFINES = Defines()