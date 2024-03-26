+++
author = "Szymon Miks"
title = "Test Doubles in Python unit tests"
description = "Explore the concept of Test Doubles in unit tests, learn how to effectively utilize them"
date = "2024-02-12"
image = "img/elena-rouame-9JU2CKqtw0M-unsplash.jpg"
categories = [
     "Python", "Software_Development", "Testing"
]
tags = [
    "python",
    "software development",
    "unit testing",
    "testing",
    "test doubles",
    "mock",
    "stub",
    "spy",
    "fake",
    "dummy",
]
draft = false
+++

## Intro

[My previous blog post](https://blog.szymonmiks.pl/p/exploring-different-schools-of-unit-testing-in-python/) was about
schools of unit testing. I mentioned there that when it comes to unit testing, ensuring that your code behaves as expected is crucial
However, sometimes it's challenging to isolate units of code for testing, especially when they depend on external services, databases, or other complex dependencies.
This is where the concept of **"Test Doubles"** comes in handy.


## What are Test Doubles?

Test Doubles are objects that stand in for real dependencies in your unit tests.
They allow you to isolate the code under test by providing controlled responses to method calls or by simulating the behavior of real objects.
There are several types of Test Doubles:

- **Mocks**: Objects that record the interactions they have with your code during a test. They can be programmed to return specific values or simulate exceptions.
- **Stubs**: Objects that provide predetermined responses to method calls. They are used to control the behavior of dependencies without executing their actual logic.
- **Fakes**: Simplified implementations of real dependencies that are used in place of the actual implementation. They are usually lighter and faster, making tests more efficient.
- **Spies**: Objects that record information about the interactions they have with your code, similar to mocks, but with a focus on observing behavior rather than controlling it.
- **Dummies**: Objects that are passed around but never actually used. They are typically used to fill parameter lists to satisfy method signatures.


## Examples

Before I show you the code examples, I want to mention one important thing.

As with `design patterns` - they were categorized, and named to introduce shared language between software engineers.
You don't have to explicitly name your object `SomethingStrategy` to tell the readers of your code that it is an implementation of a strategy design pattern.
Behavior/purpose plays the game.

I'm highlighting it because most test doubles can be implemented using `unittest.mock` and a `Mock` object from Python's standard library.
So each of them will have a connection with the word "Mock".

Ok let's go to the code, I will use the code example from my previous blog post.

```python
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
```

I omitted some parts of the code from the tests. They have no impact on the example and are an information burden.

### Mock

In this example, we want to coordinate `TransactionValidator` to raise an exception.
On the other hand, we want to check if the validation was performed once and was performed on the provided account.

```python {hl_lines=[5:6 12]}
def test_can_not_process_transaction_if_amount_bigger_than_limit() -> None:
    account = Account(1, 100.0)
    ...
    validator_mock = Mock(spec_set=TransactionValidator)
    validator_mock.validator_for.side_effect = TransactionError
    ...
    processor = TransactionProcessor(database, validator_mock, event_bus)

    with pytest.raises(TransactionError):
        processor.process_transaction(account.account_id, 100.0)

    validator_mock.validator_for.assert_called_once_with(account.account_id, 100.0)
```


### Stub

In this example, we are not checking any interactions, we tell `AccountLimit` to return a predefined value.

```python {hl_lines=[2:3]}
def test_should_validate_if_amount_bigger_than_limit() -> None:
    account_limit_stub = Mock(spec_set=AccountLimit)
    account_limit_stub.get_for.return_value = 100
    validator = TransactionValidator(account_limit_stub)

    with pytest.raises(TransactionError):
        validator.validator_for(1, 150)
```

### Fake

In this example, we are replacing `AccountDatabase` with an in-memory implementation of it.

```python
# interface
class AccountDatabase(ABC):
    @abstractmethod
    def get(self, account_id: int) -> Account:
        pass

    @abstractmethod
    def save(self, account: Account) -> None:
        pass

# implementation
class InMemoryAccountDatabase(AccountDatabase):
    def __init__(self) -> None:
        self._accounts: Dict[int, Account] = {}

    def get(self, account_id: int) -> Account:
        return copy.deepcopy(self._accounts[account_id])

    def save(self, account: Account) -> None:
        self._accounts[account.account_id] = copy.deepcopy(account)
```


```python {hl_lines=[4 9 15]}
def test_can_process_transaction_classical() -> None:
    # given
    account = Account(1, 100.0)
    database_fake = InMemoryAccountDatabase()
    ...
    processor = TransactionProcessor(database_fake, TransactionValidator(account_limit), event_bus)

    # and
    database_fake.save(account)

    # when
    processor.process_transaction(account.account_id, 50.0)

    # then
    account = database_fake.get(account.account_id)
    assert account.transaction_counter == 1
    assert account.balance == 50.0
```

### Spy

In this example, we want to be sure that an event about successful transaction processing is not sent when it should not be.

```python {hl_lines=[4 12]}
def test_can_not_process_transaction_if_amount_bigger_than_limit() -> None:
    # given
    account = Account(1, 100.0)
    event_bus_spy = Mock(spec_set=EventBus)
    processor = TransactionProcessor(database, TransactionValidator(account_limit), event_bus)
    ...

    # when
    with pytest.raises(TransactionError):
        processor.process_transaction(account.account_id, 100.0)

    event_bus_spy.dispatch.assert_not_called()
```

### Dummy

In this example, lets consider that we have a AWS Lambda handler.
Each lambda handler requires two arguments at the beginning - **event** and **context**.
From testing purpose context is never used, so we can use dummy as a replacement for it.

```python {hl_lines=[6]}
def test_can_handle_historic_summary() -> None:
    # given
    lambda_event = {}

    # when
    result = handle_historic_summary(lambda_event, Mock())

    assert result
    ...
```


## Test Doubles - best practices

I want to highlight some good practices when it comes to working with Test Doubles.
These principles allow you to have effective and maintainable test suites.
Here are some key guidelines to keep in mind:

### Don't Mock What You Don't Own:

Avoid mocking external dependencies that you don't control, such as third-party libraries or system components.
Mocking external dependencies can lead to brittle tests that break when the external API changes.
Instead, focus on mocking interfaces or abstractions that you own and control within your application.

I created a [decided post](https://www.instagram.com/p/C1KG-CJCg1i) on my Instagram about it.

### Loose Specification:
When setting up mocks, prefer loose specifications over strict ones.
A loose specification allows for flexibility in the behavior of the Test Double, accommodating changes in the implementation without requiring frequent updates to the tests.

### Don't Mock Private Methods:

Avoid mocking private methods of the class under test.
Mocking private methods can lead to tightly coupled tests that are sensitive to implementation details.
Instead, focus on testing the public interface of the class, as it represents the contract between the class and its consumers.

### Don't Break Demeter's Law for Mocks:

Adhere to Demeter's Law when setting expectations on mocks.
Demeter's Law states that a method should only call methods of its immediate dependencies, not the dependencies of its dependencies.
Breaking this principle by setting complex expectations on mocks can result in tests that are tightly coupled to the internal implementation of the class under test, making them fragile and difficult to maintain.
If you don't follow this rule, you will end up in a Mock's hell situation. Mock returns a mock that returns a mock and so on.

## Summary

Test Doubles are invaluable tools for writing effective unit tests.
Whether you're using mocks, stubs, spies, dummies, or fakes, they allow you to isolate your code and test it in controlled environments.
With Python's `unittest.mock` module, creating Test Doubles is very easy.

So next time you're writing unit tests, consider leveraging Test Doubles to ensure the reliability and maintainability of your codebase.

Happy coding!
