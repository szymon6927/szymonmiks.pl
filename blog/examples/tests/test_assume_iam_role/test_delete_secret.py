import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.assume_iam_role import LambdaEvent, SecretsManagerSdkClient, STSSdkClient
from src.assume_iam_role.delete_secret import handle
from src.assume_iam_role.errors import SecretsDeletionError


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


def test_delete_secret_should_not_raise_an_exception_if_secret_does_not_exists(
    mock_sts_client: STSSdkClient,
    mock_secrets_manager_client: SecretsManagerSdkClient,
    monkeypatch: MonkeyPatch,
    different_account_id: str,
) -> None:
    # given
    event = LambdaEvent({"secret_id": "not_existing_secret"})
    monkeypatch.setenv("ROLE_ARN_TO_ASSUME", f"arn:aws:iam::{different_account_id}:role/test_role_to_assume")

    # when
    result = handle(event, None, mock_sts_client)

    # then
    assert result == event
    assert len(mock_secrets_manager_client.list_secrets()["SecretList"]) == 1


def test_should_raise_an_error_if_secret_id_missing_in_the_event(
    mock_sts_client: STSSdkClient,
    mock_secrets_manager_client: SecretsManagerSdkClient,
    monkeypatch: MonkeyPatch,
    different_account_id: str,
) -> None:
    # given
    event = LambdaEvent({})
    monkeypatch.setenv("ROLE_ARN_TO_ASSUME", f"arn:aws:iam::{different_account_id}:role/test_role_to_assume")

    # expect
    with pytest.raises(SecretsDeletionError):
        handle(event, None, mock_sts_client)
