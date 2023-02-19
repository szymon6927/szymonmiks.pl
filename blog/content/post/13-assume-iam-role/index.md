+++
author = "Szymon Miks"
title = "How to assume an IAM role to access another AWS account"
description = "How to assume an IAM role using Python and boto3 SDK to access another AWS account."
date = "2023-02-18"
image = "img/sigmund-_dJCBtdUu74-unsplash.jpg"
categories = [
     "Python", "Software_Development", "AWS"
]
tags = [
    "python",
    "software development",
    "boto3",
    "AWS",
    "cloud services",
]
draft = false
+++

## Intro

[AWS](https://aws.amazon.com/) is one of the most popular cloud service providers nowadays.
During the writing of this blog post, AWS has **~33%** of the market, so it's very probably you will work with AWS, or you're already working with them :wink:.

In today's blog post, I will show you how to assume an IAM role using Python and `boto3` library to access another AWS account.

Sometimes you need to access something from a **different** AWS account. It is called **cross account access**.
For example, you may want to get a secret from the [secrets manager](https://aws.amazon.com/secrets-manager/).
By default, it is not possible, but AWS comes with a solution.
You can **assume the role** that has permission to the actions you want to do.
Once you do this, you can act on the other account.

You can read more about it [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html).

This blog post will be different,
I'm not going to go into details about what **[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** is,
or what **[iam role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)** is.
Instead, I will jump straight to the code.


## Code

I will use the example from the `intro` section. We want to delete a secret from the secrets manager on a different AWS account.

The code together with the tests is also available on my GitHub [here](https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/src/assume_iam_role) :rocket:.

```python
# blog/examples/src/assume_iam_role/delete_secret.py

import os
from typing import Any

import structlog
from boto3 import Session
from botocore.exceptions import ClientError

from src.assume_iam_role import LambdaEvent, SecretsManagerSdkClient, STSSdkClient
from src.assume_iam_role.errors import SecretsDeletionError

LOGGER = structlog.get_logger()


def handle(event: LambdaEvent, context: Any, sts_sdk_client: STSSdkClient) -> LambdaEvent:
    if "ROLE_ARN_TO_ASSUME" not in os.environ:
        return event

    try:
        secret_id = event["secret_id"]

        response = sts_sdk_client.assume_role(
            RoleArn=os.environ["ROLE_ARN_TO_ASSUME"],
            RoleSessionName="blogpost-delete-secret",
        )

        session = Session(
            aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
            aws_session_token=response["Credentials"]["SessionToken"],
        )
        client: SecretsManagerSdkClient = session.client("secretsmanager")

        LOGGER.info(f"Deleting secret from secretsmanager! secret_id={secret_id}")
        response = client.delete_secret(SecretId=secret_id, ForceDeleteWithoutRecovery=True)  # type: ignore
        LOGGER.info(f"Successful request! Response = {response}")
        return event
    except ClientError as error:
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            return event

        LOGGER.error(f"An error occurred during request to SecretsManager service. Error = {error}")
        raise SecretsDeletionError
    except Exception as error:
        LOGGER.error(f"An unknown error occurred during `delete_secret.handle` function execution. Error = {error}")
        raise SecretsDeletionError

```

and the test:

```python
# blog/examples/tests/test_assume_iam_role/conftest.py

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

```

---

```python
from _pytest.monkeypatch import MonkeyPatch

from src.assume_iam_role import LambdaEvent, SecretsManagerSdkClient, STSSdkClient
from src.assume_iam_role.delete_secret import handle

def test_can_delete_secret_using_assumed_role(
    mock_sts_client: STSSdkClient,
    mock_secrets_manager_client: SecretsManagerSdkClient,
    monkeypatch: MonkeyPatch,
    secret_id: str,
    different_account_id: str,
) -> None:
    # given
    event = LambdaEvent({"secret_id": secret_id})
    monkeypatch.setenv("ROLE_ARN_TO_ASSUME", f"arn:aws:iam::{different_account_id}:role/test_role_to_assume")

    # when
    result = handle(event, None, mock_sts_client)

    # then
    assert result == event
    assert mock_secrets_manager_client.list_secrets()["SecretList"] == []

```


That’s it. As simple as that :smile:.

Happy coding :wink: .
