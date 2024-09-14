from typing import List
import mido
class MidiEvent:
    def __init__(self, identity, track, channel, begin_when, end_when, note, volume):
        self.identity = identity
        self.track = track
        self.channel = channel
        self.begin_when = begin_when
        self.end_when = end_when
        self.note = note
        self.volume = volume

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
    def __init__(self, events: List[MidiEvent], tracks: List[MidiTrack], channels: List[MidiChannel]):
        self.events = events
        self.tracks = tracks
        self.channels = channels


class MidiMapper:
    @staticmethod
    def map_to_midi_file(file: str) -> MidiFile:

        midi = mido.MidiFile(file)

        events = []
        tracks = []
        channels = set()

        for i, track in enumerate(midi.tracks):
            tracks.append(MidiTrack(number=i, origin=track.name if hasattr(track, 'name') else 'Unknown'))

            current_time = 0
            note_on_events = {}
            ids = 0
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on_events[(msg.note, msg.channel)] = (current_time, msg.velocity)
                    channels.add(MidiChannel(number=msg.channel))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if (msg.note, msg.channel) in note_on_events:
                        begin_when, volume = note_on_events.pop((msg.note, msg.channel))
                        events.append(MidiEvent(
                            identity=ids,
                            track=i,
                            channel=msg.channel,
                            begin_when=begin_when,
                            end_when=current_time,
                            note=msg.note,
                            volume=volume
                        ))
                        ids += 1

        return MidiFile(
            events=events,
            tracks=tracks,
            channels=list(channels)
        )