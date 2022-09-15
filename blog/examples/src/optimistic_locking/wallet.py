import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum, unique
from typing import Any

from src.optimistic_locking.errors import InsufficientBalance, WrongCurrency

WalletSnapshot = dict[str, Any]


@unique
class Currency(Enum):
    GBP = "GBP"
    EUR = "EUR"
    CAD = "CAD"


@dataclass(frozen=True)
class Version:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Version can not be smaller than 0!")

    @classmethod
    def zero(cls) -> "Version":
        return cls(0)


class Wallet:
    def __init__(
        self,
        id: str,
        balance: Decimal,
        currency: Currency,
        created_at: datetime = datetime.utcnow(),
        version: Version = Version.zero(),
    ) -> None:
        self._id = id
        self._balance = balance
        self._currency = currency
        self._created_at = created_at
        self._version = version

    @classmethod
    def create(cls, currency: Currency) -> "Wallet":
        return cls(id=uuid.uuid4().hex, balance=Decimal(0), currency=currency)

    @property
    def id(self) -> str:
        return self._id

    @property
    def balance(self) -> Decimal:
        return self._balance

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def version(self) -> int:
        return self._version.value

    def increase_balance(self, how_much: Decimal, currency: Currency) -> None:
        if currency != self._currency:
            raise WrongCurrency("Given currency is different than currency currently assigned to the wallet!")

        self._balance += how_much

    def decrease_balance(self, how_much: Decimal, currency: Currency) -> None:
        if currency != self._currency:
            raise WrongCurrency("Given currency is different than currency currently assigned to the wallet!")

        balance = self._balance - how_much

        if balance < 0:
            raise InsufficientBalance(
                f"Can not decrease balance by `{how_much}` because the current balance is `{self._balance}`. Balance is not sufficient"
            )

        self._balance = balance

    def to_snapshot(self) -> WalletSnapshot:
        return {
            "id": self._id,
            "balance": self._balance,
            "currency": self._currency.value,
            "created_at": self._created_at.isoformat(),
            "version": self._version.value,
        }

    def __str__(self) -> str:
        return f"Wallet(id={self._id}, balance={self._balance}, currency={self._currency}, version={self._version})"
