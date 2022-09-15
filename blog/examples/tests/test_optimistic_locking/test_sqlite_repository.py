from decimal import Decimal
from sqlite3 import Connection

import pytest

from src.optimistic_locking.errors import OptimisticLockingError
from src.optimistic_locking.sqlite_wallet_repository import SQLiteWalletRepository
from src.optimistic_locking.wallet import Currency, Wallet
from tests.test_optimistic_locking.conftest import someone_modified_the_wallet_in_the_meantime


def test_can_get_wallet(sqlite_mock_connection: Connection, wallet: Wallet) -> None:
    # given
    repository = SQLiteWalletRepository(sqlite_mock_connection)
    repository.create_new(wallet)

    # when
    fetched_wallet = repository.get(wallet.id)

    # then
    assert isinstance(wallet, Wallet)
    assert fetched_wallet.to_snapshot() == wallet.to_snapshot()


def test_can_update_wallet(sqlite_mock_connection: Connection, wallet: Wallet) -> None:
    # given
    repository = SQLiteWalletRepository(sqlite_mock_connection)
    repository.create_new(wallet)

    # when
    wallet.increase_balance(Decimal(122), Currency.GBP)

    # and
    repository.update(wallet)
    fetched_wallet = repository.get(wallet.id)

    # then
    assert fetched_wallet.balance == 122


def test_can_save_wallet(sqlite_mock_connection: Connection, wallet: Wallet) -> None:
    # given
    repository = SQLiteWalletRepository(sqlite_mock_connection)

    # when
    repository.create_new(wallet)

    # then
    cursor = sqlite_mock_connection.cursor()
    assert len(cursor.execute("SELECT * FROM wallets").fetchall()) == 1


def test_optimistic_locking_works(sqlite_mock_connection: Connection, wallet: Wallet) -> None:
    # given
    repository = SQLiteWalletRepository(sqlite_mock_connection)
    repository.create_new(wallet)

    # when
    wallet = repository.get(wallet.id)

    # and
    someone_modified_the_wallet_in_the_meantime(repository, wallet.id)

    # and
    wallet.increase_balance(Decimal(1526), Currency.GBP)

    # then
    with pytest.raises(OptimisticLockingError):
        repository.update(wallet)
