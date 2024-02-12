+++
author = "Szymon Miks"
title = "Exploring Different Schools of Unit Testing in Python"
description = "Comparison of Classical and London schools of unit testing with examples written in Python"
date = "2024-01-23"
image = "img/ivan-aleksic-PDRFeeDniCk-unsplash.jpg"
categories = [
     "Python", "Software_Development", "Testing"
]
tags = [
    "python",
    "software development",
    "unit testing",
    "testing",
    "Classical school of unit testing",
    "London school of unit testing"
]
draft = false
+++

## Intro

Unit testing is a crucial aspect of software development that ensures the reliability and correctness of individual components within a system.
Over the years, different schools of thought have emerged, each with its own principles and practices.
In this blog post, I will show you two schools of unit testing: the Classical and London schools.
Through Python code examples, I will illustrate the key concepts associated with each approach.

## What is a unit?

When it comes to unit tests we want to test a certain unit, but what is this unit?
Is it one class? Multiple classes? Or maybe the whole module?

This is the key point of a discussion about Classical and London School of unit testing.

In the Classical School, a "unit" typically refers to a class or a set of classes working together to perform a specific functionality.
It is oriented toward behaviors.
The emphasis is on testing the state changes of these classes after invoking certain actions.
This approach assumes limited usage of mock or any other kind of test doubles.
They should be used only for shared dependencies or dependencies that change the state.
By "shared" dependency, I mean a dependency used by different components in our system.

In the London School, a "unit" is often defined as an individual class.
The focus shifts towards testing the interactions and collaborations between objects rather than the internal state or behaviors.
Mock objects play a significant role in isolating these interactions during testing.
This approach assumes that all dependencies internal/external/shared should be replaced by mock or any other kind of test doubles.

**Note:**
If you're interested in exploring types of test doubles further, such as mocks, stubs, fakes, and others please let me know in the comment section below.
I'm eager to create another article about it.

## Historical Background

**The Classical school** (aka. Chicago or Detroit), associated with the "state-based" or "classical" approach, originated with Kent Beck, a key figure in the Agile and XP movements.
The focus is on testing based on the observed state of an object after an action, influenced by Beck's work on the "xUnit" testing framework.

**The London school**, known as the "interaction-based" or "mockist" approach, gained prominence with developers like Steve Freeman and Nat Pryce.
They introduced the concept of using mock objects to test interactions between components, emphasizing interactions over state.

## Differences between Classical and London Schools

### Classical School

- **Focus**: Emphasizes testing based on the observed behaviors/state of objects.
- **Approach**: Tests often involve arranging objects, performing actions, and asserting the expected state.
- **Pros**:
  - Intuitive for straightforward state-based testing.
  - Simple setup and verification.
- **Cons**:
  - Test is more coupled to implementation details.
  - Tests can be brittle to changes in the internal structure.

### London School

- **Focus**: Prioritizes testing the interactions between objects.
- **Approach**: Utilizes mock objects to verify the expected behavior and interactions.
- **Pros**:
  - Encourages loose coupling and better separation of concerns.
  - More resilient to changes in internal implementations.
- **Cons**:
  - Learning curve for those new to mocking concepts.
  - Tests might be less readable due to increased setup.

## Code Examples

Consider an example of transaction processing.
The code example is trivial purposely to illustrate the difference between these two schools.

```python
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
    def __init__(
        self,
        database: InMemoryAccountDatabase,
        validator: TransactionValidator,
        event_bus: EventBus
    ) -> None:
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
```

_All code available [here](https://github.com/szymon6927/szymonmiks.pl/blob/master/blog/examples/src/classical_vs_london/example.py)_

Tests:

```python
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
```

_All tests available [here](https://github.com/szymon6927/szymonmiks.pl/blob/master/blog/examples/tests/test_classical_vs_london/test_transaction_processor.py)_

As you can see I used mock for `EventBus` inside `test_can_process_transaction_classical`.
`EventBus` is a shared dependency, it will be used by other components of my system.
From Classical School point of view it is fine to mock such dependencies.
The other two `AccountDatabase` and `TransactionValidator` are private dependencies of my `TransactionProcessor` class.
They will not be used by other components of my system. That's why I don't want to mock them.

On the other hand, London School tells us to mock every dependency of the class we are testing.
It does not matter if it is private or shared.

## Which one to choose?

It's important to highlight that there is no "one and only" approach.
The choice depends on project requirements, and a balance may be necessary.

Each of the schools has its advantages.

The Classical School - tests better reflect the actual behavior of the system.

The London Schools - tests are better isolated, and writing mocks may be easier than creating a complicated object.

I'm not the purist in this case but in my opinion, I favor Classical School.
I've seen too many mocks overuse.
Mock that returns a mock that returns a mock.

On the other hand, I can imagine a situation where using London School will be more appropriate.
For example CRUD logic.

## Summary

In the realm of Python unit testing, the Classical and London schools offer distinct approaches, each with its own set of advantages and drawbacks.
Whether you prefer the state-based simplicity of Classical testing or the interaction-based flexibility of the London school, the key is to choose an approach that aligns with your project's needs.
As you delve into the world of unit testing, consider the historical context and the practical examples provided to make informed decisions for robust and effective testing in your Python projects.
