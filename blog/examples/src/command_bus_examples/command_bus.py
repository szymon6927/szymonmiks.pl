from abc import ABC, abstractmethod
from typing import Type

from src.command_bus_examples.command import Command
from src.command_bus_examples.custom_types import HandlerType


class CommandBus(ABC):
    @abstractmethod
    def register_handler(self, command: Type[Command], handler: HandlerType) -> None:
        pass

    @abstractmethod
    def execute(self, command: Command) -> None:
        pass
