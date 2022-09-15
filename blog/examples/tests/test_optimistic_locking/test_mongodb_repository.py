from decimal import Decimal

import pytest
from pymongo.database import Database

from src.optimistic_locking.errors import OptimisticLockingError
from src.optimistic_locking.mongo_wallet_repository import MongoDBWalletRepository
from src.optimistic_locking.wallet import Currency, Wallet
from tests.test_optimistic_locking.conftest import someone_modified_the_wallet_in_the_meantime


def test_can_get_wallet(mongodb_mock: Database, wallet: Wallet) -> None:
    # given
    repository = MongoDBWalletRepository(mongodb_mock)
    repository.create_new(wallet)

    # when
    fetched_wallet = repository.get(wallet.id)

    # then
    assert isinstance(wallet, Wallet)
    assert fetched_wallet.to_snapshot() == wallet.to_snapshot()


def test_can_update_wallet(mongodb_mock: Database, wallet: Wallet) -> None:
    # given
    repository = MongoDBWalletRepository(mongodb_mock)
    repository.create_new(wallet)

    # when
    wallet.increase_balance(Decimal(122), Currency.GBP)

    # and
    repository.update(wallet)
    fetched_wallet = repository.get(wallet.id)

    # then
    assert fetched_wallet.balance == 122


def test_can_save_wallet(mongodb_mock: Database, wallet: Wallet) -> None:
    # given
    repository = MongoDBWalletRepository(mongodb_mock)

    # when
    repository.create_new(wallet)

    # then
    assert mongodb_mock["wallets"].count_documents({}) == 1


def test_optimistic_locking_works(mongodb_mock: Database, wallet: Wallet) -> None:
    # given
    repository = MongoDBWalletRepository(mongodb_mock)
    repository.create_new(wallet)

    # when
    wallet = repository.get(wallet.id)

    # and
    someone_modified_the_wallet_in_the_meantime(repository, wallet.id)

    # and
    wallet.increase_balance(Decimal(356), Currency.GBP)

    # then
    with pytest.raises(OptimisticLockingError):
        repository.update(wallet)
