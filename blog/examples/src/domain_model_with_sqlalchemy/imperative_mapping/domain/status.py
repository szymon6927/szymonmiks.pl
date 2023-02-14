from enum import Enum, unique
from typing import Tuple


@unique
class Status(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

    def __composite_values__(self) -> Tuple[str]:
        return (self.value,)
