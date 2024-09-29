from typing import List
class DynamicMidiData:
    def __init__(self,
                 current_tick: int = 0,
                 tempo: int = 500000,
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
        self.channel_colors = ['red', 'blue', 'violet', 'white', 'red', 'blue', 'violet', 'white', 'red', 'blue', 'violet', 'white', 'red', 'blue', 'violet', 'white'] if channel_colors is None else channel_colors
        self.channel_programs = [0] * 16 if channel_colors is None else channel_programs
        self.duration_ticks = duration_ticks
        self.ticks_before = 1000
        self.ticks_after = 1000