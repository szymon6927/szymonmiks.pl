from datetime import datetime

from chili import asdict
from sqlalchemy import CHAR, Column, DateTime, String, null, select
from sqlalchemy.dialects.sqlite.json import JSON
from sqlalchemy.orm import Session

from src.outbox_pattern.outbox.message import MessageType, OutboxMessage
from src.outbox_pattern.outbox.message_outbox import IMessageOutbox
from src.outbox_pattern.shared.db import Base
from src.outbox_pattern.shared.entity_id import EntityId
from src.outbox_pattern.shared.event import Event


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    id = Column(CHAR(32), primary_key=True)
    occurred_on = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    processed_on = Column(DateTime)

    def __str__(self) -> str:
        return (
            f"OutboxMessage(id={self.id}, occurred_on={self.occurred_on}, "
            f"type={self.type}, processed_on={self.processed_on})"
        )


class SqlAlchemyMessageOutbox(IMessageOutbox):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_outbox_message(self, model: OutboxMessageModel) -> OutboxMessage:
        return OutboxMessage(
            id=EntityId.of(model.id),
            occurred_on=model.occurred_on,
            type=MessageType(model.type),
            data=model.data,
            processed_on=model.processed_on,
        )

    def save(self, event: Event) -> None:
        data = asdict(event)
        outbox_message = OutboxMessageModel(
            id=str(EntityId.new_one()),
            occurred_on=datetime.utcnow(),
            type=f"{type(event).__module__}.{type(event).__name__}",
            data=data,
        )
        self._session.add(outbox_message)

    def to_publish(self) -> list[OutboxMessage]:
        stmt = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.processed_on == null())
            .order_by(OutboxMessageModel.occurred_on)
            .limit(100)
        )

        models: list[OutboxMessageModel] = self._session.execute(stmt).scalars().all()

        result = []
        for model in models:
            result.append(self._to_outbox_message(model))

        return result

    def mark_as_published(self, message: OutboxMessage) -> None:
        self._session.merge(
            OutboxMessageModel(
                id=str(message.id),
                occurred_on=message.occurred_on,
                type=str(message.type),
                data=message.data,
                processed_on=datetime.utcnow(),
            )
        )
        self._session.flush()
