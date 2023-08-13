from unittest.mock import Mock

import pytest

from src.command_bus_examples.errors import CommandAlreadyRegistered, HandlerNotFound
from src.command_bus_examples.simple_command_bus import SimpleCommandBus
from tests.test_command_buses.fixtures import NotRegisteredCommand, RegisterUser, RegisterUserHandler


def test_can_not_register_the_same_command_twice() -> None:
    # given
    command_bus = SimpleCommandBus()
    command_bus.register_handler(RegisterUser, RegisterUserHandler())

    # expect
    with pytest.raises(CommandAlreadyRegistered):
        command_bus.register_handler(RegisterUser, RegisterUserHandler())


def test_should_raise_an_error_if_trying_to_execute_not_registered_command() -> None:
    # given
    command_bus = SimpleCommandBus()

    # expect
    with pytest.raises(HandlerNotFound):
        command_bus.execute(NotRegisteredCommand())


def test_can_execute_command_successfully() -> None:
    # given
    command_bus = SimpleCommandBus()
    handler_mock = Mock(spec_set=RegisterUserHandler)
    command_bus.register_handler(RegisterUser, handler_mock)

    # when
    command_bus.execute(RegisterUser("test@test.com"))

    # then
    handler_mock.assert_called_once_with(RegisterUser("test@test.com"))
