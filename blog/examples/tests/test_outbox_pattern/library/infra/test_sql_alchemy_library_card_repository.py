from sqlalchemy.orm import Session

from src.outbox_pattern.library.domain.date_range import DateRange
from src.outbox_pattern.library.domain.library_card import LibraryCard, Status
from src.outbox_pattern.library.infra.sql_alchemy_library_card_repository import SqlAlchemyLibraryCardRepository
from src.outbox_pattern.shared.entity_id import EntityId


def test_can_save_and_get_library_card(session: Session) -> None:
    # given
    card = LibraryCard(EntityId.new_one(), EntityId.new_one(), [], Status.ACTIVE)
    repo = SqlAlchemyLibraryCardRepository(session)

    # when
    card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())
    card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())
    card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())
    repo.save(card)

    # then
    library_card = repo.get(card.id)
    assert isinstance(library_card, LibraryCard)
    assert library_card == card
