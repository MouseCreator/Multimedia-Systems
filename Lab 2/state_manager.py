from state import ProgramState


class ProgramStateManager:

    def __init__(self):
        self.state = self.load_state()

    def load_state(self):
        state = ProgramState()
        settings_map = self.read_state_file()
        if 'is_looping' in settings_map:
            state.is_looping = self.bool_attribute(settings_map, 'is_looping')
        if 'play_speed' in settings_map:
            state.play_speed = float(settings_map['play_speed'])
        if 'skip_forward_seconds' in settings_map:
            state.skip_forward_seconds = float(settings_map['skip_forward_seconds'])
        if 'skip_back_seconds' in settings_map:
            state.skip_back_seconds = float(settings_map['skip_back_seconds'])
        if 'volume' in settings_map:
            state.volume = float(settings_map['volume'])
        if 'play_on_load' in settings_map:
            state.play_on_load = self.bool_attribute(settings_map, 'play_on_load')
        if 'last_directory' in settings_map:
            state.last_directory = settings_map['last_directory']
        return state

    @staticmethod
    def bool_attribute(settings, name):
        return settings[name].lower() == 'true'

    @staticmethod
    def read_state_file():
        result = {}
        file_path = "resources/user/data.input"
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip()

        return result

    def access(self):
        return self.state


program_state_manager = None


class State:
    @staticmethod
    def get():
        if not hasattr(State, "_instance"):
            State._instance = ProgramStateManager()
        return State._instance


class PlayerService:
    @staticmethod
    def state_from_file(filename):
        if not filename:
            return False
        state = State.get().access()
        state.track.track_name = filename
        state.track.track_file = filename
        state.track.is_playing = state.play_on_load
        return True

