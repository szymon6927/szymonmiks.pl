from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from src.outbox_pattern.shared.entity_id import EntityId


@dataclass(frozen=True)
class MessageType:
    qualified_name: str

    def module_name(self) -> str:
        without_class_name = self.qualified_name.split(".")[:-1]
        return ".".join(without_class_name)

    def class_name(self) -> str:
        return self.qualified_name.split(".")[-1]

    def __str__(self) -> str:
        return self.qualified_name


@dataclass
class OutboxMessage:
    id: EntityId
    occurred_on: datetime
    type: MessageType
    data: dict[str, Any]
    processed_on: Optional[datetime]
