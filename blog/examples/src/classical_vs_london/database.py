import copy
from abc import ABC, abstractmethod
from typing import Dict

from src.classical_vs_london.account import Account


class AccountDatabase(ABC):
    @abstractmethod
    def get(self, account_id: int) -> Account:
        pass

    @abstractmethod
    def save(self, account: Account) -> None:
        pass


class InMemoryAccountDatabase(AccountDatabase):
    def __init__(self) -> None:
        self._accounts: Dict[int, Account] = {}

    def get(self, account_id: int) -> Account:
        return copy.deepcopy(self._accounts[account_id])

    def save(self, account: Account) -> None:
        self._accounts[account.account_id] = copy.deepcopy(account)


class AccountLimit(ABC):
    @abstractmethod
    def get_for(self, account_id: int) -> float:
        pass

    @abstractmethod
    def add_for(self, account_id: int, limit: float) -> None:
        pass


class InMemoryAccountLimit(AccountLimit):
    def __init__(self) -> None:
        self._limits: Dict[int, float] = {}

    def get_for(self, account_id: int) -> float:
        return self._limits.get(account_id, 10_000.0)

    def add_for(self, account_id: int, limit: float) -> None:
        self._limits[account_id] = limit
