import json
import logging
from logging import Logger
from pathlib import Path
from typing import Generator

import boto3
import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from moto.moto_server.threaded_moto_server import ThreadedMotoServer
from mypy_boto3_athena.client import AthenaClient as AthenaSdkClient

from src.athena.athena_client import AthenaClient, AthenaClientConfig, AthenaQuery

MOTO_STANDALONE_SERVER_PORT = 5001
MOTO_STANDALONE_SERVER_URL = f"http://localhost:{MOTO_STANDALONE_SERVER_PORT}"


@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch: MonkeyPatch) -> None:
    """Mocked AWS Credentials for moto."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")


def _add_data_to_athena(response_file_name: str) -> None:
    athena_responses_fixture_path = Path(__file__).parent / "fixtures"
    response = athena_responses_fixture_path / response_file_name

    requests.post(f"{MOTO_STANDALONE_SERVER_URL}/moto-api/reset")
    resp = requests.post(
        f"{MOTO_STANDALONE_SERVER_URL}/moto-api/static/athena/query-results",
        json=json.loads(response.read_text()),
    )
    assert resp.status_code == 201


@pytest.fixture
def athena_sdk() -> Generator[AthenaSdkClient, None, None]:
    server = ThreadedMotoServer(port=MOTO_STANDALONE_SERVER_PORT)
    server.start()

    athena_client = boto3.client(
        "athena",
        region_name="eu-west-1",
        endpoint_url=MOTO_STANDALONE_SERVER_URL,
    )
    yield athena_client

    server.stop()


@pytest.fixture
def test_logger() -> Logger:
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)

    return logger


def test_can_execute_query(athena_sdk: AthenaSdkClient, test_logger: Logger) -> None:
    # given
    _add_data_to_athena("example_athena_response.json")
    client = AthenaClient(
        sdk=athena_sdk,
        config=AthenaClientConfig(
            s3_output_location="s3://my-bucket/query-results",
        ),
        logger=test_logger,
    )
    query = AthenaQuery(database_name="dummy_database", sql_statement="select * from my_dummy_table;")

    # when
    client.execute(query)

    # then
    assert query.is_successful
    assert len(query.result) == 4


def test_can_execute_multiple_queries(athena_sdk: AthenaSdkClient, test_logger: Logger) -> None:
    # given
    _add_data_to_athena("example_athena_response.json")
    client = AthenaClient(
        sdk=athena_sdk,
        config=AthenaClientConfig(
            s3_output_location="s3://my-bucket/query-results",
        ),
        logger=test_logger,
    )
    query_a = AthenaQuery(database_name="dummy_database", sql_statement="select * from my_dummy_table;")
    query_b = AthenaQuery(database_name="dummy_database", sql_statement="select * from my_dummy_table;")

    # when
    client.execute_many(query_a, query_b)

    # then
    assert query_a.is_successful
    assert query_b.is_successful
