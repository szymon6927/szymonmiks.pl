from abc import ABC, abstractmethod

from src.domain_model_with_sqlalchemy.separate_model.domain.entity_id import EntityId
from src.domain_model_with_sqlalchemy.separate_model.domain.library_card import LibraryCard


class ILibraryCardRepository(ABC):
    @abstractmethod
    def get(self, library_card_id: EntityId) -> LibraryCard:
        pass

    @abstractmethod
    def save(self, library_card: LibraryCard) -> None:
        pass
