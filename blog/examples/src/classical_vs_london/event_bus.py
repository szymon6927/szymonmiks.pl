from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    pass


@dataclass(frozen=True)
class TransactionProcessed(Event):
    account_id: int


class EventBus(ABC):
    @abstractmethod
    def dispatch(self, event: Event) -> None:
        pass
