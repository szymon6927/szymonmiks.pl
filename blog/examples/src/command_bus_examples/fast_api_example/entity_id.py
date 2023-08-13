import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class EntityId:
    value: uuid.UUID

    @classmethod
    def new_one(cls) -> "EntityId":
        return EntityId(uuid.uuid4())

    @classmethod
    def of(cls, id: str) -> "EntityId":
        return cls(uuid.UUID(hex=id, version=4))

    def __str__(self) -> str:
        return self.value.hex
