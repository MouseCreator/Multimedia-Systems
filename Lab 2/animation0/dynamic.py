from typing import List

class Defaults:
    @staticmethod
    def channel_count():
        return 16
    @staticmethod
    def tempo():
        return 500000

    @staticmethod
    def time_before():
        return -1000


class DynamicMidiData:
    def __init__(self,
                 current_tick: int = 0,
                 tempo: int = Defaults.tempo(),
                 ticks_per_beat: int = 48,
                 pixels_per_tick: int = 0.65,
                 ticks_lookahead: int = 800,
                 duration_ticks:int = 0,
                 channel_colors: List[str] = None,
                 channel_programs: List[int] = None
                 ):
        self.current_tick = current_tick
        self.current_tempo = tempo
        self.ticks_per_beat = ticks_per_beat
        self.ticks_lookahead = ticks_lookahead
        self.pixels_per_tick = pixels_per_tick
        self.default_colors = ['red', 'blue', 'violet', 'cyan',
                               'pink', 'yellow', 'green', 'brown',
                               'coral', 'cyan4', 'fuchsia', 'gold3',
                               'grey14', 'IndianRed4', 'lavender', 'LightBlue3']
        self.channel_colors = list(self.default_colors) if channel_colors is None else channel_colors
        self.channel_programs = [0] * Defaults.channel_count() if channel_colors is None else channel_programs
        self.duration_ticks = duration_ticks
        self.ticks_before = 0
        self.ticks_after = 1000