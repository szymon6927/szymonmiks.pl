from typing import Dict, Type

from src.command_bus_examples.command import Command
from src.command_bus_examples.command_bus import CommandBus
from src.command_bus_examples.custom_types import HandlerType
from src.command_bus_examples.errors import CommandAlreadyRegistered, HandlerNotFound


class SimpleCommandBus(CommandBus):
    def __init__(self) -> None:
        self._handlers: Dict[Type[Command], HandlerType] = {}

    def register_handler(self, command: Type[Command], handler: HandlerType) -> None:
        if command in self._handlers:
            raise CommandAlreadyRegistered.for_command(command.__name__)

        self._handlers[command] = handler

    def execute(self, command: Command) -> None:
        try:
            handler = self._handlers[type(command)]
            handler(command)
        except KeyError:
            raise HandlerNotFound.for_command(command)
