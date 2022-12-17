import sqlite3
from decimal import Decimal
from sqlite3 import Connection
from typing import Iterator

import boto3
import pytest
from mongomock import MongoClient
from moto import mock_dynamodb
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from pymongo.database import Database
from pytest import MonkeyPatch

from src.optimistic_locking.repository import IWalletRepository
from src.optimistic_locking.wallet import Currency, Wallet


@pytest.fixture()
def wallet_dynamodb_table_mock(monkeypatch: MonkeyPatch) -> Iterator[Table]:
    with mock_dynamodb():
        monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
        table_name = "wallet"

        dynamodb_client: DynamoDBClient = boto3.client("dynamodb")
        dynamodb_resource: DynamoDBServiceResource = boto3.resource("dynamodb")

        dynamodb_client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}, {"AttributeName": "created_at", "KeyType": "RANGE"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        table = dynamodb_resource.Table(table_name)

        yield table

        dynamodb_client.delete_table(TableName=table_name)


@pytest.fixture()
def mongodb_mock() -> Iterator[Database]:
    mongo_client: MongoClient = MongoClient()

    database = mongo_client.get_database("optimistic_locking")

    yield database

    mongo_client.drop_database("optimistic_locking")


@pytest.fixture()
def sqlite_mock_connection() -> Iterator[Connection]:
    connection = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)

    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE wallets(id TEXT PRIMARY KEY, balance TEXT, currency TEXT, created_at TEXT, version INTEGER)"
    )
    cursor.close()

    yield connection

    connection.close()


@pytest.fixture()
def wallet(currency: Currency = Currency.GBP) -> Wallet:
    wallet = Wallet.create(currency)
    return wallet


def someone_modified_the_wallet_in_the_meantime(repo: IWalletRepository, wallet_id: str) -> None:
    wallet = repo.get(wallet_id)
    wallet.increase_balance(Decimal(222), Currency.GBP)
    repo.update(wallet)
