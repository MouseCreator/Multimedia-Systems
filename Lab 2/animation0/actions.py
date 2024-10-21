from MusicPlayer import MusicPlayer, ProgramMessage, BeginMessage, EndMessage, ControlMessage
from midis import MidiEvent, SoundEvent, ProgramChangeEvent, TempoEvent, ControlChangeEvent
from typing import List
from abc import ABC, abstractmethod
from dynamic import DynamicMidiData

class MidiAction(ABC):
    @abstractmethod
    def begin_when(self):
        pass

    @abstractmethod
    def end_when(self):
        pass
    @abstractmethod
    def is_long_lasting(self) -> bool:
        pass

    @abstractmethod
    def created_by_id(self):
        pass

    def on_register(self):
        pass

    def on_press(self):
        pass

    def on_forced_register(self):
        self.on_register()

    def on_forced_press(self):
        self.on_press()

    def on_release(self):
        pass


class SoundAction(MidiAction):

    def __init__(self, sound_event: SoundEvent, animation_handler, music_player: MusicPlayer):
        self.sound_event = sound_event
        self.animation_handler = animation_handler
        self.music_player = music_player

    def on_register(self):
        self.animation_handler.on_register(self.sound_event)

    def on_press(self):
        self.animation_handler.on_press(self.sound_event)
        self.music_player.enqueue(
            BeginMessage(self.sound_event.note, self.sound_event.channel, self.sound_event.volume))

    def on_release(self):
        self.animation_handler.on_release(self.sound_event)
        self.music_player.enqueue(EndMessage(self.sound_event.note, self.sound_event.channel))

    def begin_when(self):
        return self.sound_event.begin_when

    def end_when(self):
        return self.sound_event.end_when

    def created_by_id(self):
        return self.sound_event.identity

    def on_forced_register(self):
        self.animation_handler.on_register(self.sound_event)
    def on_forced_press(self):
        self.animation_handler.on_press(self.sound_event)
    def is_long_lasting(self):
        return False

class TempoAction(MidiAction):

    def created_by_id(self):
        return self.tempo_event.identity

    def begin_when(self):
        return self.tempo_event.begin_when

    def end_when(self):
        return self.tempo_event.begin_when

    def __init__(self, tempo_event: TempoEvent, dynamics: DynamicMidiData):
        self.tempo_event = tempo_event
        self.dynamics = dynamics

    def on_press(self):
        self.dynamics.current_tempo = self.tempo_event.tempo
    def is_long_lasting(self):
        return True


class ProgramAction(MidiAction):
    def created_by_id(self):
        return self.program_event.identity

    def begin_when(self):
        return self.program_event.begin_when

    def end_when(self):
        return self.program_event.begin_when

    def __init__(self, event: ProgramChangeEvent, dynamics: DynamicMidiData, music_player: MusicPlayer):
        self.program_event = event
        self.dynamics = dynamics
        self.music_player = music_player

    def on_press(self):
        channel = self.program_event.channel
        program = self.program_event.program
        self.dynamics.channel_programs[channel] = program
        self.music_player.enqueue(ProgramMessage(program, channel))

    def is_long_lasting(self):
        return True


class ControlAction(MidiAction):
    def created_by_id(self):
        return self.control_event.identity

    def begin_when(self):
        return self.control_event.begin_when

    def end_when(self):
        return self.control_event.begin_when

    def __init__(self, control_event: ControlChangeEvent, music_player: MusicPlayer):
        self.control_event = control_event
        self.music_player = music_player

    def on_press(self):
        channel = self.control_event.channel
        control = self.control_event.control
        value = self.control_event.value
        self.music_player.enqueue(ControlMessage(control, value, channel))

    def is_long_lasting(self):
        return True


class ActionFactory:
    def __init__(self, animation_handler, dynamics: DynamicMidiData, music_player: MusicPlayer):
        self.animation_handler = animation_handler
        self.dynamics = dynamics
        self.music_player = music_player

    def create_action(self, event: MidiEvent) -> MidiAction:
        if isinstance(event, SoundEvent):
            return self._create_sound_action(event)
        elif isinstance(event, ProgramChangeEvent):
            return self._create_program_action(event)
        elif isinstance(event, TempoEvent):
            return self._create_tempo_action(event)
        elif isinstance(event, ControlChangeEvent):
            return self._create_control_action(event)
        else:
            raise Exception(f"Unknown event to convert: {event}")

    def _create_sound_action(self, sound_event: SoundEvent) -> SoundAction:
        return SoundAction(sound_event, self.animation_handler, self.music_player)

    def _create_program_action(self, program_change_event: ProgramChangeEvent) -> ProgramAction:
        return ProgramAction(program_change_event, self.dynamics, self.music_player)

    def _create_control_action(self, control_change_event: ControlChangeEvent) -> ControlAction:
        return ControlAction(control_change_event, self.music_player)

    def _create_tempo_action(self, event: TempoEvent) -> TempoAction:
        return TempoAction(event, self.dynamics)

    def create_all_actions(self, events: List[MidiEvent]) -> List[MidiAction]:
        actions = []
        for event in events:
            action = self.create_action(event)
            actions.append(action)
        return actions