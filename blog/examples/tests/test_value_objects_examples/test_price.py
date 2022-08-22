from decimal import Decimal

import pytest

from src.value_object_examples.price import Price


def test_can_not_create_price_with_value_smaller_than_0() -> None:
    # expect
    with pytest.raises(ValueError):
        Price.of(-5)


def test_can_add() -> None:
    # expect
    assert Price.of(5) + Price.of(5) == Price.of(10)
    assert Price.of(5.10) + Price.of(10.00) == Price(Decimal("15.1"))


def test_can_sub() -> None:
    # expect
    assert Price.of(10) - Price.of(5) == Price.of(5)
    assert Price.of(22.5) - Price.of(2.5) == Price.of(20)
    with pytest.raises(ValueError):
        Price.of(20) - Price.of(30)


def test_can_mull() -> None:
    # expect
    assert Price.of(10) * Price.of(10) == Price.of(100)
    assert Price.of(14.5) * Price.of(2) == Price.of(29)


def test_can_calculate_discount() -> None:
    # given
    price = Price.of(100)

    # when
    discount_price = price.discount(20)

    # then
    assert discount_price == Price.of(20)
