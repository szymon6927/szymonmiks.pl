import uuid
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class EntityId:
    value: uuid.UUID

    def __composite_values__(self) -> Tuple[str]:
        return (str(self),)

    @classmethod
    def new_one(cls) -> "EntityId":
        return EntityId(uuid.uuid4())

    @classmethod
    def of(cls, id: str) -> "EntityId":
        return cls(uuid.UUID(hex=id, version=4))

    def __str__(self) -> str:
        return self.value.hex
