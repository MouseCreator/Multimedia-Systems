class ProgramState:
    def __init__(self):
        self.is_playing = False
        self.is_looping = False
        self.play_speed = 1.0
        self.skip_forward_seconds = 10
        self.skip_back_seconds = 10
        self.volume = 100
        self.play_on_load = True
        self.last_directory = "C:\\"
        self.preferred_width = 800
        self.preferred_height = 600
        self.preferred_x = 100
        self.preferred_y = 100
