import os
from typing import Generator

import boto3
import pytest
from _pytest.monkeypatch import MonkeyPatch
from moto import mock_secretsmanager, mock_sts

from src.assume_iam_role import SecretsManagerSdkClient, STSSdkClient


@pytest.fixture(autouse=True)
def aws_envs() -> None:
    os.environ["AWS_REGION"] = "eu-west-1"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "XXX"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "XXX"


@pytest.fixture()
def different_account_id() -> str:
    return "111111111111"


@pytest.fixture()
def secret_id() -> str:
    return "/test/secret/blogpost/szymonmiks"


@pytest.fixture()
def mock_sts_client() -> Generator[STSSdkClient, None, None]:
    with mock_sts():
        client: STSSdkClient = boto3.client("sts")
        yield client


@pytest.fixture()
def mock_secrets_manager_client(
    secret_id: str, monkeypatch: MonkeyPatch, different_account_id: str
) -> Generator[SecretsManagerSdkClient, None, None]:
    with mock_secretsmanager():
        # http://docs.getmoto.org/en/latest/docs/multi_account.html#configure-an-account-using-sts
        monkeypatch.setenv("MOTO_ACCOUNT_ID", different_account_id)
        client: SecretsManagerSdkClient = boto3.client("secretsmanager")
        client.create_secret(Name=secret_id)

        yield client
