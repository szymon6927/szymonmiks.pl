from typing import Any, NewType

from mypy_boto3_secretsmanager import SecretsManagerClient
from mypy_boto3_sts import STSClient

LambdaEvent = NewType("LambdaEvent", dict[str, Any])

STSSdkClient = STSClient
SecretsManagerSdkClient = SecretsManagerClient
