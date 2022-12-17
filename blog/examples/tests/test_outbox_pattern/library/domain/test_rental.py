import pytest

from src.outbox_pattern.library.domain.date_range import DateRange
from src.outbox_pattern.library.domain.rental import Rental
from src.outbox_pattern.shared.entity_id import EntityId


def test_can_not_prolong_for_more_than_7_days() -> None:
    # given
    rental = Rental.create(EntityId.new_one(), DateRange.one_week())

    # then
    with pytest.raises(ValueError):
        rental.prolong(8)
