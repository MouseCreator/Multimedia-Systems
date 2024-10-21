from actions import MidiAction, TempoAction, ProgramAction, ControlAction
from dynamic import DynamicMidiData
from typing import List
from abc import ABC, abstractmethod
from utils import IntPair

class MidiNavigatorState:
    pressed_list : List[MidiAction]
    created_list : List[MidiAction]
    def __init__(self,
                 created_pointer = 0,
                 pressed_pointer = 0,
                 created_list = None,
                 pressed_list = None,
                 ):
        if created_list is None:
            created_list = []
        if pressed_list is None:
            pressed_list = []
        self.pressed_list = list(pressed_list)
        self.created_list = list(created_list)
        self.created_pointer = created_pointer
        self.pressed_pointer = pressed_pointer


class MidiNavigator(ABC):
    pointer_limit: int
    actions: List[MidiAction]
    dynamic : DynamicMidiData
    def on_load_file(self, actions: List[MidiAction]):
        self.actions = list(actions)
        self.pointer_limit = len(actions)
    def on_unload_file(self):
        self.actions = []
        self.pointer_limit = 0
    @abstractmethod
    def set_time_to(self, time_ticks) -> MidiNavigatorState:
        pass

    def _common_movement(self, time_ticks, initial_state : MidiNavigatorState) -> MidiNavigatorState:
        created_pointer = initial_state.created_pointer
        pressed_pointer = initial_state.pressed_pointer
        pressed_list = list(initial_state.pressed_list)
        created_list = list(initial_state.created_list)
        updated_into_notes = time_ticks
        created_map = self._to_event_id_map(created_list)

        while created_pointer < self.pointer_limit:
            event = self.actions[created_pointer]
            if updated_into_notes + self.dynamic.ticks_lookahead >= event.begin_when():
                created_map[event.created_by_id()] = event
                created_pointer += 1
            else:
                break
        pressed = self._to_event_id_map(pressed_list)
        while pressed_pointer < self.pointer_limit:
            event = self.actions[pressed_pointer]
            if updated_into_notes >= event.begin_when():
                pressed[event.created_by_id()] = event
                pressed_pointer += 1
            else:
                break
        unpressed_list = []
        for event in pressed.values():
            if event.is_long_lasting():
                continue
            elif updated_into_notes >= event.end_when():
                unpressed_list.append(event.created_by_id())

        for key in unpressed_list:
            pressed.pop(key)
        created_actual = self._to_event_list(created_map)
        return MidiNavigatorState(
            created_pointer=created_pointer,
            pressed_pointer=pressed_pointer,
            created_list=created_actual,
            pressed_list=pressed_list
        )

    def _to_event_id_map(self, lst):
        emap = {}
        for m in lst:
            emap[m.created_by_id()] = m
        return emap
    def _to_event_list(self, emap):
        return list(emap.values())


class SimpleMidiNavigator(MidiNavigator):
    def __init__(self, dynamic : DynamicMidiData):
        self.pointer_limit = 0
        self.actions = []
        self.dynamic = dynamic

    def set_time_to(self, time_ticks) -> MidiNavigatorState:
        initial_state = MidiNavigatorState()
        return self._common_movement(time_ticks, initial_state)

class MidiCachePartitionBuilder:
    def __init__(self, actions : List[MidiAction], dynamic : DynamicMidiData):
        self.last_tempo_action = None
        self.created = {}
        self.pressed = {}
        self.dynamic = dynamic
        self.actions = actions
        self.program_changes = {}
        self.control_changes = {}
        self.created_pointer = 0
        self.pressed_pointer = 0
        self.pointer_limit = len(actions)
        self.time_ticks = 0
    def release_state(self) -> MidiNavigatorState:
        state = MidiNavigatorState()
        state.created_list = list(self.created.values())
        if self.last_tempo_action is not None:
            state.pressed_list.append(self.last_tempo_action)
        for change in self.program_changes.values():
            state.pressed_list.append(change)
        for change in self.control_changes.values():
            state.pressed_list.append(change)
        for pressed_key in self.pressed.values():
            state.pressed_list.append(pressed_key)
        state.created_pointer = self.created_pointer
        state.pressed_pointer = self.pressed_pointer
        return state

    def _record_tempo_change(self, tempo_message : TempoAction):
        self.last_tempo_action = tempo_message
    def _record_program_change(self, program_change : ProgramAction):
        event = program_change.program_event
        self.program_changes[event.channel] = program_change
    def _record_control_change(self, control_change : ControlAction):
        event = control_change.control_event
        key = IntPair(event.channel, event.control)
        self.control_changes[key] = control_change

    def _on_press_action(self, action : MidiAction):
        if isinstance(action, TempoAction):
            self._record_tempo_change(action)
            return
        if isinstance(action, ProgramAction):
            self._record_program_change(action)
            return
        if isinstance(action, ControlAction):
            self._record_control_change(action)
            return
        self.pressed[action.created_by_id()] = action
    def is_finished(self):
        return self.pressed_pointer >= self.pointer_limit
    def move_partition(self, by_ticks):
        self.time_ticks += by_ticks
        while self.created_pointer < self.pointer_limit:
            event = self.actions[self.created_pointer]
            if self.time_ticks + self.dynamic.ticks_lookahead >= event.begin_when():
                self.created[event.created_by_id()] = event
                self.created_pointer += 1
            else:
                break
        while self.pressed_pointer < self.pointer_limit:
            event = self.actions[self.pressed_pointer]
            if self.time_ticks >= event.begin_when():
                self.created.pop(event.created_by_id())
                self._on_press_action(event)
                self.pressed_pointer += 1
            else:
                break
        to_pop = []
        for event in self.pressed.values():
            if self.time_ticks >= event.end_when() and event.created_by_id() in self.pressed.keys():
                to_pop.append(event.created_by_id())

        for key in to_pop:
            self.pressed.pop(key)


class CachingMidiNavigator(MidiNavigator):
    partitions: List[MidiNavigatorState]
    def __init__(self, dynamic : DynamicMidiData, partition_length=1000):
        self.pointer_limit = 0
        self.actions = []
        self.dynamic = dynamic
        self.partition_length = partition_length
        self.partitions = []

    def set_time_to(self, time_ticks) -> MidiNavigatorState:
        partition_id = time_ticks // self.partition_length
        total_partitions = len(self.partitions)
        if partition_id < 0:
            partition_id = 0
        if partition_id >= total_partitions:
            partition_id = total_partitions - 1
        current_partition = self.partitions[partition_id]
        state = self._common_movement(time_ticks, current_partition)
        return state

    def _split_input(self):
        builder = MidiCachePartitionBuilder(self.actions, self.dynamic)
        while not builder.is_finished():
            state = builder.release_state()
            self.partitions.append(state)
            builder.move_partition(self.partition_length)



    def on_load_file(self, actions: List[MidiAction]):
        super().on_load_file(actions)
        self._split_input()

    def on_unload_file(self):
        super().on_unload_file()
        self.partitions = []



