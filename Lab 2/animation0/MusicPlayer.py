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
        self.queue = []
    def start(self):
        self.port = mido.open_output()
        self.queue = []

    def _message_priority(self, message : PlayingMessage):
        if isinstance(message, ProgramMessage):
            return 0
        elif isinstance(message, EndMessage):
            return 1
        elif isinstance(message, BeginMessage):
            return 2
        else:
            return 3
    def _play(self, source : PlayingMessage):
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
    def enqueue(self, message : PlayingMessage):
        self.queue.append(message)
    def play_queue(self):
        sorted_queue = sorted(self.queue,key = self._message_priority)
        for message in sorted_queue:
            self._play(message)
    def clear_queue(self):
        self.queue.clear()
    def play_and_clear(self):
        self.play_queue()
        self.clear_queue()

    def close(self):
        self.port.close()


