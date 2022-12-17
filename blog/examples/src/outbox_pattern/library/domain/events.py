from dataclasses import dataclass
from datetime import datetime

from src.outbox_pattern.shared.event import Event


@dataclass(frozen=True)
class LibraryCardCreated(Event):
    card_id: str
    owner_id: str


@dataclass(frozen=True)
class ItemRented(Event):
    resource_id: str
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class LibraryCardSuspended(Event):
    card_id: str
    owner_id: str


@dataclass(frozen=True)
class ItemProlonged(Event):
    resource_id: str
    prolonged_for: int
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class ItemReturned(Event):
    resource_id: str
