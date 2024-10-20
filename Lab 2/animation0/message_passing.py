from abc import ABC, abstractmethod
from typing import List, Dict

class Message(ABC):
    @abstractmethod
    def topic(self) -> str:
        pass


class ControlMessage(Message):
    # play, pause
    def __init__(self, control):
        self.control = control
    def topic(self):
        return "control"
class TickMessage(Message):
    # move to tick
    def __init__(self, tick):
        self.tick = tick
    def topic(self) -> str:
        return "tick"

class TopicConfig:
    single_message_topic : List[str]
    multi_message_topic : List[str]


class MessagePassing:
    topics_map: [str, str]
    single_message_map: Dict[str, Message]
    multi_message_map: Dict[str, List[Message]]
    def configure_topics(self, config : TopicConfig):
        self.topics_map = {}
        self.single_message_map = {}
        self.multi_message_map = {}
        for single in config.single_message_topic:
            self.topics_map[single] = "single"
        for multi in config.multi_message_topic:
            self.topics_map[multi] = "multi"
            self.multi_message_map[multi] = []
    def post_message(self, message : Message):
        topic = message.topic()
        map_type = self.topics_map.get(topic, "none")
        if map_type == "single":
            self.single_message_map[topic] = message
        elif map_type == "multi":
            self.multi_message_map[topic].append(message)
        else:
            raise Exception(f"Unknown topic type: {topic}")

    def is_topic_empty(self, topic : str) -> bool:
        map_type = self.topics_map.get(topic, "none")
        if map_type == "single":
            return not topic in self.single_message_map
        elif map_type == "multi":
            return not len(self.multi_message_map[topic])
        else:
            raise Exception(f"Unknown topic type: {topic}")
    def pop_message(self, topic : str) -> Message | None:
        map_type = self.topics_map.get(topic, "none")
        if map_type == "single":
            return self.single_message_map.pop(topic, None)
        elif map_type == "multi":
            lst = self.multi_message_map[topic]
            if not lst:
                return None
            return lst.pop(0)
        else:
            raise Exception(f"Unknown topic type: {topic}")