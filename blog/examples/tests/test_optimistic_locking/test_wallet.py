from decimal import Decimal

import pytest

from src.optimistic_locking.errors import InsufficientBalance, WrongCurrency
from src.optimistic_locking.wallet import Currency, Wallet


def test_can_create_wallet() -> None:
    # given
    wallet = Wallet.create(Currency.GBP)

    # then
    assert isinstance(wallet, Wallet)
    assert wallet.balance == 0


def test_can_increase_balance() -> None:
    # given
    wallet = Wallet.create(Currency.GBP)

    # when
    wallet.increase_balance(Decimal(150), Currency.GBP)

    # then
    assert wallet.balance == 150


def test_can_not_increase_balance_if_different_currency() -> None:
    # given
    wallet = Wallet.create(Currency.GBP)

    # expect
    with pytest.raises(WrongCurrency):
        wallet.increase_balance(Decimal(150), Currency.CAD)


def test_can_decrease_balance() -> None:
    # given
    wallet = Wallet.create(Currency.GBP)
    wallet.increase_balance(Decimal(150), Currency.GBP)

    # and
    wallet.decrease_balance(Decimal(50), Currency.GBP)

    # then
    assert wallet.balance == 100


def test_can_not_decrease_balance_if_different_currency() -> None:
    # given
    wallet = Wallet.create(Currency.GBP)
    wallet.increase_balance(Decimal(150), Currency.GBP)

    # expect
    with pytest.raises(WrongCurrency):
        wallet.decrease_balance(Decimal(50), Currency.CAD)


def test_can_not_decrease_balance_to_less_than_zero() -> None:
    # given
    wallet = Wallet.create(Currency.GBP)
    wallet.increase_balance(Decimal(122), Currency.GBP)

    # expect
    with pytest.raises(InsufficientBalance):
        wallet.decrease_balance(Decimal(222), Currency.GBP)
