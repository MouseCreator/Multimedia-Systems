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
class ControlMessage(PlayingMessage):
    def __init__(self, control, value, channel):
        self.control = control
        self.channel = channel
        self.value = value

class MusicPlayer:

    def __init__(self):
        self.port = None
        self.queue = []
    def start(self):
        self.port = mido.open_output()
        self.queue = []

    def _message_priority(self, message : PlayingMessage):
        priority = 0
        priority_list = [ProgramMessage, ControlMessage, EndMessage, BeginMessage]
        for p in priority_list:
            if isinstance(message, p):
                break
            priority += 1
        return priority

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
        elif isinstance(source, ControlMessage):
            msg = mido.Message('control_change', control=source.control, channel=source.channel, time=0, value=source.value)
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


