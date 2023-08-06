from typing import List, Tuple
from datetime import datetime
from abc import ABC, abstractmethod


class LogEntry(object):
    def __init__(self, app: str, instance: str, topic: str, log_events: List[Tuple[datetime, str]]):
        self.app = app
        self.instance = instance
        self.topic = topic
        self.log_events = log_events


class ICloudLogger(ABC):
    @classmethod
    @abstractmethod
    def write(cls, log_entry: LogEntry):
        pass
