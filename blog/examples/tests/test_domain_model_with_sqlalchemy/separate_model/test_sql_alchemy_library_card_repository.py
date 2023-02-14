import pytest
from sqlalchemy.orm import Session

from src.domain_model_with_sqlalchemy.errors import BorrowingError, ResourceNotFound
from src.domain_model_with_sqlalchemy.separate_model.domain.date_range import DateRange
from src.domain_model_with_sqlalchemy.separate_model.domain.entity_id import EntityId
from src.domain_model_with_sqlalchemy.separate_model.domain.library_card import LibraryCard, Status
from src.domain_model_with_sqlalchemy.separate_model.infrastructure.sql_alchemy_library_card_repository import (
    SqlAlchemyLibraryCardRepository,
)


def test_can_save_and_get_library_card(session: Session) -> None:
    # given
    owner_id = EntityId.new_one()
    card_id = EntityId.new_one()
    card = LibraryCard(card_id, owner_id, [], Status.ACTIVE)
    repo = SqlAlchemyLibraryCardRepository(session)

    # when
    card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())
    card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())
    card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())
    repo.save(card)

    # then
    library_card = repo.get(card.id)
    assert isinstance(library_card, LibraryCard)
    assert library_card.id == card_id
    assert library_card.is_active()
    assert library_card.is_owned_by(owner_id)
    with pytest.raises(BorrowingError):
        library_card.borrow(resource_id=EntityId.new_one(), how_long=DateRange.one_week())


def test_should_raise_an_error_if_library_card_not_found(session: Session) -> None:
    # given
    card = LibraryCard(EntityId.new_one(), EntityId.new_one(), [], Status.ACTIVE)
    repo = SqlAlchemyLibraryCardRepository(session)

    # expect
    with pytest.raises(ResourceNotFound):
        repo.get(card.id)
