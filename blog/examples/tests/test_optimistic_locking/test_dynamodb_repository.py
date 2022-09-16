from decimal import Decimal

import pytest
from mypy_boto3_dynamodb.service_resource import Table

from src.optimistic_locking.dynamodb_wallet_repository import DynamoDBWalletRepository
from src.optimistic_locking.errors import OptimisticLockingError, WalletNotFound
from src.optimistic_locking.wallet import Currency, Wallet
from tests.test_optimistic_locking.conftest import someone_modified_the_wallet_in_the_meantime


def test_can_get_wallet(wallet_dynamodb_table_mock: Table, wallet: Wallet) -> None:
    # given
    repository = DynamoDBWalletRepository(wallet_dynamodb_table_mock)
    repository.create(wallet)

    # when
    fetched_wallet = repository.get(wallet.id)

    # then
    assert isinstance(wallet, Wallet)
    assert fetched_wallet.to_snapshot() == wallet.to_snapshot()


def test_should_raise_an_error_if_wallet_not_found(wallet_dynamodb_table_mock: Table) -> None:
    # given
    repository = DynamoDBWalletRepository(wallet_dynamodb_table_mock)

    # expect
    with pytest.raises(WalletNotFound):
        repository.get("12345")


def test_can_update_wallet(wallet_dynamodb_table_mock: Table, wallet: Wallet) -> None:
    # given
    repository = DynamoDBWalletRepository(wallet_dynamodb_table_mock)
    repository.create(wallet)

    # when
    wallet.increase_balance(Decimal(100), Currency.GBP)

    # and
    repository.update(wallet)
    fetched_wallet = repository.get(wallet.id)

    # then
    assert fetched_wallet.balance == 100


def test_can_save_wallet(wallet_dynamodb_table_mock: Table, wallet: Wallet) -> None:
    # given
    repository = DynamoDBWalletRepository(wallet_dynamodb_table_mock)

    # when
    repository.create(wallet)

    # then
    assert wallet_dynamodb_table_mock.scan()["Count"] == 1
    assert wallet_dynamodb_table_mock.scan()["Items"][0] == wallet.to_snapshot()


def test_optimistic_locking_works(wallet_dynamodb_table_mock: Table, wallet: Wallet) -> None:
    # given
    repository = DynamoDBWalletRepository(wallet_dynamodb_table_mock)
    repository.create(wallet)

    # when
    wallet = repository.get(wallet.id)

    # and
    someone_modified_the_wallet_in_the_meantime(repository, wallet.id)

    # and
    wallet.increase_balance(Decimal(52), Currency.GBP)

    # then
    with pytest.raises(OptimisticLockingError):
        repository.update(wallet)
