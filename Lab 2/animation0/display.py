from midis import MidiMapper

def test_print():
    midi_file = MidiMapper.map_to_midi_file("resource/audio/overworld.mid")
    print(midi_file)

class MidiNotesDisplay:

    def __init__(self):
        pass

    def update(self):
        pass

class DisplayEvent:
    def __init__(self, note, e_type):
        self.note = note
        self.e_type = e_type

class MidiNotesState:
    def __init__(self, notes):
        self.notes = notes
        self.lookahead_millis = 1500
        self.time = 0
        self.create_queue = []
        self.slide_queue = []
        self.pressed_queue = []

    def set_time_to(self, time_millis):
        pass
    def move_time_forward(self, by_millis):
        updated_time = self.time + by_millis
        created = []
        while len(self.create_queue) > 0:
            event = self.create_queue[0]
            if updated_time - self.lookahead_millis >= event.begin_when:
                created.append(event)
                self.create_queue.pop(0)
            else:
                break
        pressed = []
        while len(self.slide_queue) > 0:
            event = self.slide_queue[0]
            if updated_time >= event.begin_when:
                pressed.append(event)
                self.slide_queue.pop(0)
            else:
                break
        unpressed = []
        for event in self.pressed_queue:
            if updated_time >= event.end_when:
                unpressed.append(event)
        for event in unpressed:
            self.pressed_queue.remove(event)
        self.time = updated_time
        display_events = []
        for event in created:
            display_events.append(DisplayEvent(event, "register"))
        for event in pressed:
            display_events.append(DisplayEvent(event, "press"))
        for event in unpressed:
            display_events.append(DisplayEvent(event, "destroy"))
        return display_events





class MidiNotesDisplayFactory:

    def create(self, filename) -> MidiNotesDisplay:
        midi_file = MidiMapper.map_to_midi_file(filename)



