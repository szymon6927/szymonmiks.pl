import uuid
from datetime import datetime
from unittest.mock import Mock

from apos import IApos
from sqlalchemy.orm import Session

from src.outbox_pattern.outbox.outbox_processor import OutboxProcessor
from src.outbox_pattern.outbox.sql_alchemy_message_outbox import SqlAlchemyMessageOutbox
from tests.test_outbox_pattern.conftest import SomethingImportantHappened


def test_process_messages(session: Session) -> None:
    # given
    message_outbox = SqlAlchemyMessageOutbox(session)
    processor = OutboxProcessor(message_outbox, session, Mock(spec_set=IApos))

    # when
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.now(), message="test message 1")
    )
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.now(), message="test message 2")
    )
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.now(), message="test message 3")
    )
    session.commit()

    # and
    processor.process_outbox_message()

    # then
    assert message_outbox.to_publish() == []
