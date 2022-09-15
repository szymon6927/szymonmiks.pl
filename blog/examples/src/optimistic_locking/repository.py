from abc import ABC, abstractmethod

from src.optimistic_locking.wallet import Wallet


class IWalletRepository(ABC):
    @abstractmethod
    def create_new(self, wallet: Wallet) -> Wallet:
        pass

    @abstractmethod
    def get(self, wallet_id: str) -> Wallet:
        pass

    @abstractmethod
    def update(self, wallet: Wallet) -> None:
        pass
