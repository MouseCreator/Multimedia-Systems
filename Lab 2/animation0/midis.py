from typing import List
import mido
from abc import ABC, abstractmethod

class MidiEvent(ABC):
    identity: int
    begin_when: int

    @abstractmethod
    def event_type(self):
        pass

class SoundEvent(MidiEvent):
    def __init__(self, identity:int, track:int, channel:int, begin_when:int, end_when:int, note, volume):
        self.identity = identity
        self.track = track
        self.channel = channel
        self.begin_when = begin_when
        self.end_when = end_when
        self.note = note
        self.volume = volume
    def event_type(self):
        return "sound"

class TempoEvent(MidiEvent):
    def event_type(self):
        return "tempo"

    def __init__(self, identity: int, begin_when: int, tempo: int):
        self.identity = identity
        self.tempo = tempo
        self.begin_when = begin_when

class ProgramChangeEvent(MidiEvent):
    def __init__(self, identity:int, begin_when: int, channel: int, program: int):
        self.identity = identity
        self.begin_when = begin_when
        self.program = program
        self.channel = channel
    def event_type(self):
        return "program"

class ControlChangeEvent(MidiEvent):
    def __init__(self, identity:int, begin_when: int, channel: int, control: int, value : int):
        self.identity = identity
        self.begin_when = begin_when
        self.control = control
        self.channel = channel
        self.value = value
    def event_type(self):
        return "control"

class MidiTrack:
    def __init__(self, number, origin):
        self.number = number
        self.origin = origin
class MidiChannel:
    def __init__(self, number):
        self.number = number
    def __hash__(self):
        return self.number
    def __eq__(self, other):
        return other.number == self.number

class MidiMetaData:
    def __init__(self, tempo: int, ticks_per_beat: int, duration_ticks: int):
        self.tempo = tempo
        self.ticks_per_beat = ticks_per_beat
        self.duration_ticks = duration_ticks

class MidiFile:
    def __init__(self,
                 events: List[MidiEvent],
                 tracks: List[MidiTrack],
                 channels: List[MidiChannel],
                 metadata: MidiMetaData
                 ):
        self.events = events
        self.tracks = tracks
        self.channels = channels
        self.metadata = metadata


class MidiMapper:
    @staticmethod
    def map_to_midi_file(file: str) -> MidiFile:

        midi = mido.MidiFile(file)

        events = []
        tracks = []
        channels = set()
        duration_ticks = 0
        ids = 0
        for i, track in enumerate(midi.tracks):
            tracks.append(MidiTrack(number=i, origin=track.name if hasattr(track, 'name') else 'Unknown'))
            current_time = 0
            note_on_events = {}
            for msg in track:
                message_time = msg.time
                current_time += message_time

                if msg.type == 'note_on' and msg.velocity > 0:
                        note_on_events[(msg.note, msg.channel)] = (current_time, msg.velocity)
                        channels.add(MidiChannel(number=msg.channel))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if (msg.note, msg.channel) in note_on_events:
                        begin_when, volume = note_on_events.pop((msg.note, msg.channel))
                        events.append(SoundEvent(
                            identity=ids,
                            track=i,
                            channel=msg.channel,
                            begin_when=begin_when,
                            end_when=current_time,
                            note=msg.note,
                            volume=volume
                        ))
                        ids += 1
                elif msg.type == 'set_tempo':
                    begin_when = current_time
                    events.append(TempoEvent(ids, begin_when, msg.tempo))
                    ids += 1
                elif msg.type == 'program_change':
                    begin_when = current_time
                    events.append(ProgramChangeEvent(ids, begin_when, msg.channel, msg.program))
                    ids += 1
                elif msg.type == 'control_change':
                    begin_when = current_time
                    events.append(ControlChangeEvent(ids, begin_when, msg.channel, msg.control, msg.value))
                    ids += 1
                elif msg.type in ['track_name',
                                  'time_signature',
                                  'key_signature',
                                  'control_change',
                                  'midi_port',
                                  'end_of_track',
                                  'pitchwheel']:
                    print(msg)
                else:
                    raise Exception(f"UNKNOWN MESSAGE TYPE: {msg.type}")
            if current_time > duration_ticks:
                duration_ticks = current_time

        sorted_events_by_time = sorted(events, key=lambda event: event.begin_when)

        metadata = MidiMetaData(500000, midi.ticks_per_beat, duration_ticks)
        return MidiFile(
            events=sorted_events_by_time,
            tracks=tracks,
            channels=list(channels),
            metadata=metadata
        )