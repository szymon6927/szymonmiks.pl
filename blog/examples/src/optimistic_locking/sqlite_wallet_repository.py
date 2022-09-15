import sqlite3
from sqlite3 import Connection

from src.optimistic_locking.errors import OptimisticLockingError, RepositoryError, WalletNotFound
from src.optimistic_locking.repository import IWalletRepository
from src.optimistic_locking.wallet import Wallet
from src.optimistic_locking.wallet_mapper import WalletMapper


class SQLiteWalletRepository(IWalletRepository):
    def __init__(self, connection: Connection):
        self._connection = connection

    def create_new(self, wallet: Wallet) -> Wallet:
        snapshot = wallet.to_snapshot()
        snapshot["balance"] = str(snapshot["balance"])

        cursor = self._connection.cursor()

        columns = ", ".join(snapshot.keys())
        placeholders = ", ".join("?" * len(snapshot.values()))
        sql = "INSERT INTO wallets ({}) VALUES ({})".format(columns, placeholders)

        try:
            cursor.execute(sql, list(snapshot.values()))
        except sqlite3.Error as error:
            raise RepositoryError.create_operation_failed() from error

        return wallet

    def update(self, wallet: Wallet) -> None:
        cursor = self._connection.cursor()

        sql = "UPDATE wallets SET balance = ?, version = ? WHERE id = ? AND version = ?"
        params = (str(wallet.balance), wallet.version + 1, wallet.id, wallet.version)

        try:
            result = cursor.execute(sql, params)

            if result.rowcount == 0:
                raise OptimisticLockingError.build(wallet.id)
        except sqlite3.Error as error:
            raise RepositoryError.update_operation_failed() from error

    def get(self, wallet_id: str) -> Wallet:
        self._connection.row_factory = sqlite3.Row
        cursor = self._connection.cursor()

        sql = "SELECT * FROM wallets WHERE id = ?"
        params = (wallet_id,)

        try:
            result = cursor.execute(sql, params).fetchone()
            if not result:
                raise WalletNotFound.build(wallet_id)

            return WalletMapper.from_db_response(dict(result))
        except sqlite3.Error as error:
            raise RepositoryError.get_operation_failed() from error
