from datetime import datetime
from decimal import Decimal
from typing import Any

from src.optimistic_locking.wallet import Currency, Version, Wallet


class WalletMapper:
    @staticmethod
    def from_db_response(record: dict[str, Any]) -> Wallet:
        return Wallet(
            id=record["id"],
            balance=record["balance"] if isinstance(record["balance"], Decimal) else Decimal(record["balance"]),
            currency=Currency(record["currency"]),
            created_at=datetime.fromisoformat(record["created_at"]),
            version=Version(int(record["version"])),
        )

    @staticmethod
    def from_mongo_document(document: dict[str, Any]) -> Wallet:
        return Wallet(
            id=document["_id"],
            balance=document["balance"].to_decimal(),
            currency=Currency(document["currency"]),
            created_at=datetime.fromisoformat(document["created_at"]),
            version=Version(int(document["version"])),
        )
