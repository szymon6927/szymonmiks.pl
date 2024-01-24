from src.classical_vs_london.account import AccountType
from src.classical_vs_london.database import AccountLimit, InMemoryAccountDatabase
from src.classical_vs_london.event_bus import EventBus, TransactionProcessed


class TransactionError(Exception):
    pass


class TransactionValidator:
    def __init__(self, account_limit: AccountLimit) -> None:
        self._account_limit = account_limit

    def validator_for(self, account_id: int, amount: float) -> None:
        if amount < 0:
            raise TransactionError()

        limit = self._account_limit.get_for(account_id)

        if amount > limit:
            raise TransactionError()


class TransactionProcessor:
    def __init__(self, database: InMemoryAccountDatabase, validator: TransactionValidator, event_bus: EventBus) -> None:
        self._database = database
        self._validator = validator
        self._event_bus = event_bus

    def process_transaction(self, account_id: int, amount: float) -> None:
        self._validator.validator_for(account_id, amount)

        account = self._database.get(account_id)

        account.balance -= amount
        account.transaction_counter += 1

        if account.transaction_counter > 10:
            account.type = AccountType.VIP

        self._database.save(account)
        self._event_bus.dispatch(TransactionProcessed(account.account_id))
