from typing import List
import mido
from abc import ABC, abstractmethod

class MidiEvent(ABC):
    identity: int
    begin_when: int
    end_when: int

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


class ProgramChangeEvent(MidiEvent):
    def __init__(self, identity:int, track:int, begin_when: int, origin):
        self.identity = identity
        self.track = track
        self.begin_when = begin_when
        self.end_when = begin_when
        self.origin = origin
    def event_type(self):
        return "program"

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

class MidiFile:
    def __init__(self, events: List[MidiEvent], tracks: List[MidiTrack], channels: List[MidiChannel], duration: int):
        self.events = events
        self.tracks = tracks
        self.channels = channels
        self.duration = duration


class MidiMapper:
    @staticmethod
    def map_to_midi_file(file: str) -> MidiFile:

        midi = mido.MidiFile(file)

        events = []
        tracks = []
        channels = set()
        for i, track in enumerate(midi.tracks):
            tracks.append(MidiTrack(number=i, origin=track.name if hasattr(track, 'name') else 'Unknown'))

            tempo = 500000
            ticks_per_beat = midi.ticks_per_beat
            time_per_tick = tempo / ticks_per_beat
            current_time = 0
            note_on_events = {}
            ids = 0

            for msg in track:
                message_time = (msg.time * time_per_tick) / 1000.0
                current_time += message_time

                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on_events[(msg.note, msg.channel)] = (current_time, msg.velocity)
                    channels.add(MidiChannel(number=msg.channel))
                elif msg.type == 'note_off' and msg.velocity > 0:
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
                    time_per_tick = tempo / ticks_per_beat
                    tempo = msg.tempo
                elif msg.type == 'program_change':
                    begin_when = current_time
                    events.append(ProgramChangeEvent(ids, i, begin_when, msg.program))
                    ids += 1
        duration_ms = MidiMapper._get_duration(midi)
        sorted_events_by_time = sorted(events, key=lambda event: (event.begin_when, event.end_when))
        return MidiFile(
            events=sorted_events_by_time,
            tracks=tracks,
            channels=list(channels),
            duration=duration_ms
        )
    @staticmethod
    def _get_duration(midi_file):
        tempo = 500000 # default tempo value
        ticks_per_beat = midi_file.ticks_per_beat
        total_time_ms = 0
        for msg in midi_file:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            if msg.time > 0:
                time_per_tick_us = tempo / ticks_per_beat
                time_ms = (msg.time * time_per_tick_us) / 1000.0
                total_time_ms += time_ms

        return total_time_ms