import pytest

from src.outbox_pattern.library.domain.date_range import DateRange
from src.outbox_pattern.library.domain.errors import BorrowingError
from src.outbox_pattern.library.domain.events import ItemProlonged, ItemRented, ItemReturned, LibraryCardCreated
from src.outbox_pattern.library.domain.library_card import LibraryCard, Status
from src.outbox_pattern.library.domain.rental import Rental
from src.outbox_pattern.shared.entity_id import EntityId


def test_can_create_card() -> None:
    # given
    library_card = LibraryCard.create(EntityId.new_one())

    # then
    assert isinstance(library_card, LibraryCard)
    assert isinstance(library_card.events[0], LibraryCardCreated)


def test_can_not_borrow_if_card_not_active() -> None:
    # given
    not_active_card = LibraryCard(EntityId.new_one(), EntityId.new_one(), [], Status.SUSPENDED)

    # when
    with pytest.raises(BorrowingError):
        not_active_card.borrow(EntityId.new_one(), DateRange.one_week())


def test_can_borrow_resource() -> None:
    # given
    card = LibraryCard.create(EntityId.new_one())
    resource_id = EntityId.new_one()
    two_weeks = DateRange.two_weeks()

    # when
    card.borrow(resource_id, two_weeks)

    # then
    event = card.events[1]
    assert isinstance(event, ItemRented)
    assert event.resource_id == str(resource_id)
    assert event.starts_at == two_weeks.start_date
    assert event.ends_at == two_weeks.end_date


def test_can_not_borrow_more_than_14_days() -> None:
    # given
    card = LibraryCard.create(EntityId.new_one())

    # then
    with pytest.raises(BorrowingError):
        card.borrow(EntityId.new_one(), DateRange.one_month())


def test_can_not_borrow_more_than_3_resources() -> None:
    # given
    card = LibraryCard.create(EntityId.new_one())

    # when
    card.borrow(EntityId.new_one(), DateRange.one_week())
    card.borrow(EntityId.new_one(), DateRange.one_week())
    card.borrow(EntityId.new_one(), DateRange.one_week())

    # then
    with pytest.raises(BorrowingError):
        card.borrow(EntityId.new_one(), DateRange.one_week())


def test_can_prolong_a_resource() -> None:
    # given
    resource_id = EntityId.new_one()
    rentals = [Rental.create(resource_id, DateRange.one_week())]
    card = LibraryCard(EntityId.new_one(), EntityId.new_one(), rentals, Status.ACTIVE)
    card.borrow(resource_id, DateRange.one_week())

    # when
    card.prolong_for(rentals[0].id, 7)

    # then
    event = card.events[1]
    assert isinstance(event, ItemProlonged)
    assert event.resource_id == str(resource_id)
    assert event.prolonged_for == 7


def test_can_give_back_a_resource() -> None:
    # given
    resource_id = EntityId.new_one()
    rentals = [Rental.create(resource_id, DateRange.one_week())]
    card = LibraryCard(EntityId.new_one(), EntityId.new_one(), rentals, Status.ACTIVE)

    # when
    card.give_back(resource_id)

    # then
    event = card.events[0]
    assert isinstance(event, ItemReturned)
    assert event.resource_id == str(resource_id)
