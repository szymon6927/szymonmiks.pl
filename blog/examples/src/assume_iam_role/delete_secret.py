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
