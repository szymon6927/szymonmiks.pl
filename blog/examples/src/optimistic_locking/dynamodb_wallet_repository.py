from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import Table

from src.optimistic_locking.errors import OptimisticLockingError, RepositoryError, WalletNotFound
from src.optimistic_locking.repository import IWalletRepository
from src.optimistic_locking.wallet import Wallet
from src.optimistic_locking.wallet_mapper import WalletMapper


class DynamoDBWalletRepository(IWalletRepository):
    def __init__(self, wallet_table: Table) -> None:
        self._table = wallet_table

    def create_new(self, wallet: Wallet) -> Wallet:
        snapshot = wallet.to_snapshot()

        try:
            self._table.put_item(Item=snapshot)
        except ClientError as error:
            raise RepositoryError.create_operation_failed() from error

        return wallet

    def get(self, wallet_id: str) -> Wallet:
        try:
            response = self._table.query(KeyConditionExpression=Key("id").eq(wallet_id))

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise RepositoryError.get_operation_failed()

            if not response["Count"]:
                raise WalletNotFound(wallet_id)

            wallet = WalletMapper.from_db_response(response["Items"][0])

            return wallet
        except ClientError as error:
            raise RepositoryError.get_operation_failed() from error

    def update(self, wallet: Wallet) -> None:
        try:
            update_expression = "set balance=:balance_value, version=:version_value"

            expression_attribute_values = {
                ":balance_value": wallet.balance,
                ":version_value": wallet.version + 1,
            }

            self._table.update_item(
                Key={"id": wallet.id, "created_at": wallet.created_at.isoformat()},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,  # type: ignore
                ConditionExpression=Attr("version").eq(wallet.version),
                ReturnValues="UPDATED_NEW",
            )
        except ClientError as error:
            if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise OptimisticLockingError(wallet.id)

            raise RepositoryError.update_operation_failed() from error
