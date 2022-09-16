from bson.decimal128 import Decimal128
from pymongo.database import Database
from pymongo.errors import PyMongoError

from src.optimistic_locking.errors import OptimisticLockingError, RepositoryError, WalletNotFound
from src.optimistic_locking.repository import IWalletRepository
from src.optimistic_locking.wallet import Wallet
from src.optimistic_locking.wallet_mapper import WalletMapper


class MongoDBWalletRepository(IWalletRepository):
    def __init__(self, database: Database):
        self._collection = database.get_collection("wallets")

    def create(self, wallet: Wallet) -> Wallet:
        snapshot = wallet.to_snapshot()
        snapshot["_id"] = snapshot["id"]
        del snapshot["id"]
        snapshot["balance"] = Decimal128(snapshot["balance"])

        try:
            self._collection.insert_one(snapshot)
        except PyMongoError as error:
            raise RepositoryError.create_operation_failed() from error

        return wallet

    def update(self, wallet: Wallet) -> None:
        try:
            result = self._collection.update_one(
                {"_id": wallet.id, "version": wallet.version},
                {"$set": {"balance": Decimal128(wallet.balance), "version": wallet.version + 1}},
            )

            if result.modified_count == 0:
                raise OptimisticLockingError(wallet.id)
        except PyMongoError as error:
            raise RepositoryError.update_operation_failed() from error

    def get(self, wallet_id: str) -> Wallet:
        try:
            document = self._collection.find_one({"_id": wallet_id})

            if not document:
                raise WalletNotFound(wallet_id)

            return WalletMapper.from_mongo_document(document)
        except PyMongoError as error:
            raise RepositoryError.get_operation_failed() from error
