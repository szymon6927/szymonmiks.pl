import uuid

from sqlalchemy.orm import Session

from src.outbox_pattern.library.application.service import LibraryCardService
from src.outbox_pattern.library.infra.sql_alchemy_library_card_repository import SqlAlchemyLibraryCardRepository
from src.outbox_pattern.outbox.message import MessageType
from src.outbox_pattern.outbox.sql_alchemy_message_outbox import SqlAlchemyMessageOutbox
from src.outbox_pattern.shared.event_bus import StoreAndForwardEventBus


def test_can_create_card_and_events(session: Session) -> None:
    # given
    repo = SqlAlchemyLibraryCardRepository(session)
    message_outbox = SqlAlchemyMessageOutbox(session)
    event_bus = StoreAndForwardEventBus(message_outbox)
    service = LibraryCardService(repo, event_bus, session)

    # when
    service.create(uuid.uuid4().hex)

    # then
    messages = message_outbox.to_publish()
    assert len(messages) == 1
    assert messages[0].type == MessageType(qualified_name="src.outbox_pattern.library.domain.events.LibraryCardCreated")
