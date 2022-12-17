from sqlalchemy.orm import Session

from src.outbox_pattern.library.domain.library_card import LibraryCard
from src.outbox_pattern.library.domain.library_card_repository import ILibraryCardRepository
from src.outbox_pattern.shared.entity_id import EntityId
from src.outbox_pattern.shared.event_bus import IEventBus


class LibraryCardService:
    def __init__(self, library_card_repository: ILibraryCardRepository, event_bus: IEventBus, session: Session) -> None:
        self._library_card_repository = library_card_repository
        self._event_bus = event_bus
        self._session = session

    def create(self, owner_id: str) -> LibraryCard:
        library_card = LibraryCard.create(EntityId.of(owner_id))

        with self._session.begin():
            events = library_card.events
            self._library_card_repository.save(library_card)

            for event in events:
                self._event_bus.publish(event)

        return library_card
