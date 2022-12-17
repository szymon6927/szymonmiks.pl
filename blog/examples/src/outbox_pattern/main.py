import uuid

from src.outbox_pattern.library.application.service import LibraryCardService
from src.outbox_pattern.library.infra.sql_alchemy_library_card_repository import SqlAlchemyLibraryCardRepository
from src.outbox_pattern.outbox.sql_alchemy_message_outbox import SqlAlchemyMessageOutbox
from src.outbox_pattern.shared.db import Db
from src.outbox_pattern.shared.event_bus import StoreAndForwardEventBus


def main() -> None:
    session = Db("sqlite:///db.sqlite").session
    repo = SqlAlchemyLibraryCardRepository(session)
    message_outbox = SqlAlchemyMessageOutbox(session)
    event_bus = StoreAndForwardEventBus(message_outbox)
    service = LibraryCardService(repo, event_bus, session)

    service.create(uuid.uuid4().hex)


if __name__ == "__main__":
    main()
