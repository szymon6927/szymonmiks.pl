from enum import Enum, unique


@unique
class Status(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
