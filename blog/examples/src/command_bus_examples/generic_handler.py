from typing import Generic, TypeVar

from src.command_bus_examples.command import Command

TCommand = TypeVar("TCommand", bound=Command)


class Handler(Generic[TCommand]):
    def __call__(self, command: TCommand) -> None:
        raise NotImplementedError
