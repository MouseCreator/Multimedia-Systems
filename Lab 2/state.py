class ProgramState:
    def __init__(self):
        self.track = LoadedTrack()
        self.is_looping = False
        self.play_speed = 1.0
        self.skip_forward_seconds = 10
        self.skip_back_seconds = 10
        self.volume = 100
        self.play_on_load = True
        self.last_directory = "C:\\"
        self.preferred_width = 800
        self.preferred_height = 600

# types: audio / video / stream / none
class LoadedTrack:
    def __init__(self):
        self.type = 'audio'
        self.is_playing = False
        self.duration_seconds = 70
        self.current_second = 10
        self.track_name = "Mouse.mp3"
        self.track_file = "D:\Mouse.mp3"
