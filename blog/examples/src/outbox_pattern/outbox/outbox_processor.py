import importlib
from typing import Type

import structlog
from apos import Apos
from sqlalchemy.orm import Session
from structlog.typing import FilteringBoundLogger

from src.outbox_pattern.outbox.message import MessageType
from src.outbox_pattern.outbox.message_outbox import IMessageOutbox


class OutboxProcessor:
    def __init__(self, message_outbox: IMessageOutbox, session: Session, messenger: Apos) -> None:
        self._message_outbox = message_outbox
        self._session = session
        self._messenger = messenger
        self._logger: FilteringBoundLogger = structlog.get_logger()

    def _get_cls_for(self, message_type: MessageType) -> Type:
        module = importlib.import_module(message_type.module_name())
        return getattr(module, message_type.class_name())  # type: ignore

    def process_outbox_message(self) -> None:
        with self._session.begin():
            messages = self._message_outbox.to_publish()

            for message in messages:
                event_cls = self._get_cls_for(message.type)
                event = event_cls(**message.data)
                self._messenger.publish_event(event)
                self._logger.info(f"Publishing event {event}")
                self._message_outbox.mark_as_published(message)
