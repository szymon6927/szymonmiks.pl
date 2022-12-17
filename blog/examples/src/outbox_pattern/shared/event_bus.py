from abc import ABC, abstractmethod

from src.outbox_pattern.outbox.message_outbox import IMessageOutbox
from src.outbox_pattern.shared.event import Event


class IEventBus(ABC):
    @abstractmethod
    def publish(self, event: Event) -> None:
        pass


class StoreAndForwardEventBus(IEventBus):
    def __init__(self, message_outbox: IMessageOutbox) -> None:
        self._message_outbox = message_outbox

    def publish(self, event: Event) -> None:
        self._message_outbox.save(event)
