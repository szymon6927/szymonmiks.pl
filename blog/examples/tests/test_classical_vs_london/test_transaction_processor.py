from unittest.mock import Mock

import pytest

from src.classical_vs_london.account import Account, AccountType
from src.classical_vs_london.database import AccountDatabase, InMemoryAccountDatabase, InMemoryAccountLimit
from src.classical_vs_london.event_bus import EventBus, TransactionProcessed
from src.classical_vs_london.example import TransactionError, TransactionProcessor, TransactionValidator


def test_can_process_transaction_classical() -> None:
    # given
    account = Account(1, 100.0)
    database = InMemoryAccountDatabase()
    account_limit = InMemoryAccountLimit()
    event_bus = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, TransactionValidator(account_limit), event_bus)

    # and
    database.save(account)
    account_limit.add_for(account.account_id, 100.0)

    # when
    processor.process_transaction(account.account_id, 50.0)

    # then
    account = database.get(account.account_id)
    assert account.transaction_counter == 1
    assert account.balance == 50.0
    event_bus.dispatch.assert_called_once_with(TransactionProcessed(account.account_id))


def test_can_not_process_transaction_if_amount_bigger_than_limit_classical() -> None:
    # given
    account = Account(1, 100.0)
    database = InMemoryAccountDatabase()
    account_limit = InMemoryAccountLimit()
    event_bus = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, TransactionValidator(account_limit), event_bus)

    # and
    database.save(account)
    account_limit.add_for(account.account_id, 50.0)

    # when
    with pytest.raises(TransactionError):
        processor.process_transaction(account.account_id, 100.0)

    event_bus.dispatch.assert_not_called()


def test_should_become_vip_if_transaction_counter_reached_classical() -> None:
    # given
    account = Account(1, 100.0, 10)
    database = InMemoryAccountDatabase()
    account_limit = InMemoryAccountLimit()
    event_bus = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, TransactionValidator(account_limit), event_bus)

    # and
    database.save(account)
    account_limit.add_for(account.account_id, 100.0)

    # when
    processor.process_transaction(account.account_id, 50.0)

    # then
    account = database.get(account.account_id)
    assert account.transaction_counter == 11
    assert account.type == AccountType.VIP
    event_bus.dispatch.assert_called_once_with(TransactionProcessed(account.account_id))


def test_can_process_transaction_london() -> None:
    # given
    account = Account(1, 100.0)
    database = Mock(spec_set=AccountDatabase)
    database.get.return_value = account
    validator = Mock(spec_set=TransactionValidator)
    event_bus = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, validator, event_bus)

    # when
    processor.process_transaction(account.account_id, 50.0)

    # then
    assert account.balance == 50.0
    validator.validator_for.assert_called_once_with(account.account_id, 50.0)
    database.save.assert_called_once_with(account)
    event_bus.dispatch.assert_called_once_with(TransactionProcessed(account.account_id))


def test_can_not_process_transaction_if_amount_bigger_than_limit_london() -> None:
    # given
    account = Account(1, 100.0)
    database = Mock(spec_set=AccountDatabase)
    database.get.return_value = account
    validator = Mock(spec_set=TransactionValidator)
    validator.validator_for.side_effect = TransactionError
    event_bus = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, validator, event_bus)

    # when
    with pytest.raises(TransactionError):
        processor.process_transaction(account.account_id, 100.0)

    validator.validator_for.assert_called_once_with(account.account_id, 100.0)
    event_bus.dispatch.assert_not_called()


def test_should_become_vip_if_transaction_counter_reached_london() -> None:
    # given
    account = Account(1, 100.0, 10)
    database = Mock(spec_set=AccountDatabase)
    database.get.return_value = account
    validator = Mock(spec_set=TransactionValidator)
    event_bus = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, Mock(spec_set=TransactionValidator), event_bus)

    # when
    processor.process_transaction(account.account_id, 50.0)

    # then
    assert account.transaction_counter == 11
    assert account.type == AccountType.VIP
    validator.validator_for.assert_called_once_with(account.account_id, 50.0)
    database.save.assert_called_once_with(account)
    event_bus.dispatch.assert_called_once_with(TransactionProcessed(account.account_id))
