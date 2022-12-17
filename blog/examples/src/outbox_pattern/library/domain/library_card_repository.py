from abc import ABC, abstractmethod

from src.outbox_pattern.library.domain.library_card import LibraryCard
from src.outbox_pattern.shared.entity_id import EntityId


class ILibraryCardRepository(ABC):
    @abstractmethod
    def get(self, library_card_id: EntityId) -> LibraryCard:
        pass

    @abstractmethod
    def save(self, library_card: LibraryCard) -> None:
        pass
