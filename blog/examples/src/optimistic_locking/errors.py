class InsufficientBalance(Exception):
    pass


class WrongCurrency(Exception):
    pass


class RepositoryError(Exception):
    @classmethod
    def create_operation_failed(cls) -> "RepositoryError":
        return cls("An error occurred during adding a wallet to the database!")

    @classmethod
    def update_operation_failed(cls) -> "RepositoryError":
        return cls("An error occurred during the update operation for a wallet!")

    @classmethod
    def get_operation_failed(cls) -> "RepositoryError":
        return cls("An error occurred while retrieving the wallet!")


class WalletNotFound(Exception):
    def __init__(self, wallet_id: str) -> None:
        super().__init__(f"Wallet with id={wallet_id} was not found!")


class OptimisticLockingError(Exception):
    def __init__(self, wallet_id: str) -> None:
        super().__init__(f"Wallet {wallet_id} must have been updated in the meantime!")
