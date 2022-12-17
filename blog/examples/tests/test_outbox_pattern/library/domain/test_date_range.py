from datetime import datetime, timedelta

from src.outbox_pattern.library.domain.date_range import DateRange


def test_can_check_if_date_is_with_in_range() -> None:
    # given
    one_week = DateRange.one_week()
    one_month = DateRange.one_month()

    # expect
    assert not one_month.is_within_range(datetime.now() + timedelta(days=50))
    assert one_month.is_within_range(datetime.now() + timedelta(days=12))
    assert not one_week.is_within_range(datetime.now() + timedelta(days=15))
    assert one_week.is_within_range(datetime.now() + timedelta(days=5))
