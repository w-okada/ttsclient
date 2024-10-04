from abc import ABC, abstractmethod


class EventEmitter(ABC):
    @abstractmethod
    def emit_coroutine(self, event, data, to=None):
        pass
