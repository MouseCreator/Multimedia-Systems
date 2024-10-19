from midis import MidiFile, SoundEvent, TempoEvent, ProgramChangeEvent, MidiEvent
from dynamic import DynamicMidiData
from typing import List

class MidiNavigatorOutput:
    def __init__(self, current_tick : int,
                 fired_controls: List[MidiEvent],
                 ):
        self.current_tick = current_tick
        self.fired_controls = fired_controls

class MidiNavigator:
    sound_events: List[SoundEvent]
    control_events: List[MidiEvent]
    def __init__(self, dynamic : DynamicMidiData):
        self.dynamics = dynamic
        self.sound_events = []
        self.control_events = []
    def load(self, file : MidiFile,  ):
        self.sound_events = []
        self.control_events = []

        for event in file.events:
            if isinstance(event, SoundEvent):
                self.sound_events.append(event)
            else:
                self.control_events.append(event)
        sorted(self.sound_events, key=lambda e: e.begin_when)
        sorted(self.control_events, key=lambda e: e.begin_when)
    def unload(self):
        self.sound_events.clear()
        self.control_events.clear()
    def load_from_timestamp(self, ticks_passed) -> MidiNavigatorOutput:
        current_tick = ticks_passed
        current_lookahead = ticks_passed + self.dynamics.ticks_lookahead
        fired_controls = []
        last_tempo=None
        channels = {}
        for event in self.control_events:
            if event.begin_when > current_lookahead:
                break
            if event.begin_when < current_tick:
                if isinstance(event, TempoEvent):
                    last_tempo = event
                elif isinstance(event, ProgramChangeEvent):
                    channels[event.channel] = event
                else:
                    fired_controls.append(event)
        if last_tempo is not None:
            fired_controls.append(last_tempo)
        for value in channels.values():
            fired_controls.append(value)
        return MidiNavigatorOutput(
            current_tick=current_tick,
            fired_controls=fired_controls,
        )




