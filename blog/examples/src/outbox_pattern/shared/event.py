from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Event:
    id: str
    occurred_on: datetime
