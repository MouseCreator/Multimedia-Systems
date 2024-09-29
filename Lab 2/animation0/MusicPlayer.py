import mido
from abc import ABC
class PlayingMessage(ABC):
    pass
class BeginMessage(PlayingMessage):
    def __init__(self, note, channel, velocity):
        self.note = note
        self.channel = channel
        self.velocity = velocity
class EndMessage(PlayingMessage):
    def __init__(self, note, channel):
        self.note = note
        self.channel = channel
class ProgramMessage(PlayingMessage):
    def __init__(self, program_number, channel):
        self.program_number = program_number
        self.channel = channel

class MusicPlayer:

    def __init__(self):
        self.port = None
    def start(self):
        self.port = mido.open_output()

    def play(self, source : PlayingMessage):
        if isinstance(source, BeginMessage):
            msg = mido.Message('note_on', note=source.note, velocity=source.velocity, channel=source.channel)
            self.port.send(msg)
        elif isinstance(source, EndMessage):
            msg = mido.Message('note_off', note=source.note, velocity=0, channel=source.channel)
            self.port.send(msg)
        elif isinstance(source, ProgramMessage):
            msg = mido.Message('program_change', program=source.program_number, channel=source.channel)
            self.port.send(msg)
        else:
            raise Exception(f"Unknown message type: {source}")
    def close(self):
        self.port.close()


