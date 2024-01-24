from enum import Enum


class AccountType(Enum):
    NORMAL = "NORMAL"
    VIP = "VIP"


class Account:
    account_id: int
    balance: float
    transaction_counter: int
    type: AccountType

    def __init__(
        self, account_id: int, balance: float, counter: int = 0, account_type: AccountType = AccountType.NORMAL
    ):
        self.account_id = account_id
        self.balance = balance
        self.transaction_counter = counter
        self.type = account_type
