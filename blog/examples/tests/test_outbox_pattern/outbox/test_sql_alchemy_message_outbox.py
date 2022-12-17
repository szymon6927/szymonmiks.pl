import uuid
from datetime import datetime

from chili import asdict
from sqlalchemy.orm import Session

from src.outbox_pattern.outbox.message import MessageType
from src.outbox_pattern.outbox.sql_alchemy_message_outbox import SqlAlchemyMessageOutbox
from tests.test_outbox_pattern.conftest import SomethingImportantHappened


def test_can_save_event(session: Session) -> None:
    # given
    message_outbox = SqlAlchemyMessageOutbox(session)

    # when
    event = SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.utcnow(), message="test")
    message_outbox.save(event)

    # then
    messages = message_outbox.to_publish()
    assert len(messages) == 1
    assert isinstance(messages[0].type, MessageType)
    assert messages[0].data == asdict(event)


def test_can_get_messages_to_publish(session: Session) -> None:
    # given
    message_outbox = SqlAlchemyMessageOutbox(session)

    # when
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.utcnow(), message="test 1")
    )
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.utcnow(), message="test 2")
    )
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.utcnow(), message="test 3")
    )

    # then
    messages = message_outbox.to_publish()
    assert len(messages) == 3


def test_can_mark_message_as_published(session: Session) -> None:
    # given
    message_outbox = SqlAlchemyMessageOutbox(session)

    # when
    message_outbox.save(
        SomethingImportantHappened(id=uuid.uuid4().hex, occurred_on=datetime.utcnow(), message="test 1")
    )

    # and
    message = message_outbox.to_publish()[0]
    message_outbox.mark_as_published(message)

    # then
    assert len(message_outbox.to_publish()) == 0
