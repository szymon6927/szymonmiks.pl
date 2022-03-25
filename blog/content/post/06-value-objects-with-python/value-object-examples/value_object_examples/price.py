from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class Price:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Price can not be smaller than 0")

    @classmethod
    def zero(cls) -> "Price":
        return cls(Decimal(0))

    @classmethod
    def of(cls, value: Union[int, str, float]) -> "Price":
        return Price(Decimal(value))

    def discount(self, percentage: int) -> "Price":
        return Price(Decimal(percentage * self.value / 100))

    def __add__(self, other: "Price") -> "Price":
        return Price(self.value + other.value)

    def __sub__(self, other: "Price") -> "Price":
        return Price(self.value - other.value)

    def __mul__(self, other: "Price") -> "Price":
        return Price(self.value * other.value)

    def __str__(self) -> str:
        return f"{self.value:.2f}"
