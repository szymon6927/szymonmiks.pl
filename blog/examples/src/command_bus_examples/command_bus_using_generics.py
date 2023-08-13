from dataclasses import dataclass
from typing import Dict, Type

from src.command_bus_examples.command import Command
from src.command_bus_examples.command_bus import CommandBus
from src.command_bus_examples.custom_types import HandlerType
from src.command_bus_examples.errors import CommandAlreadyRegistered, HandlerNotFound
from src.command_bus_examples.generic_handler import Handler


@dataclass(frozen=True)
class RegisterUser(Command):
    email: str


class RegisterUserHandler(Handler[RegisterUser]):
    def __call__(self, command: RegisterUser) -> None:
        print(f"Registering {command.email}")


class CommandBusUsingGenerics(CommandBus):
    def __init__(self) -> None:
        self._handlers: Dict[Type[Command], HandlerType] = {}

    def register_handler(self, command: Type[Command], handler: HandlerType) -> None:
        if not issubclass(handler.__class__, Handler):
            raise ValueError("Handler must be a subclass of Handler[TCommand]")

        if command in self._handlers:
            raise CommandAlreadyRegistered.for_command(command.__name__)

        self._handlers[command] = handler

    def execute(self, command: Command) -> None:
        try:
            handler = self._handlers[type(command)]
            handler(command)
        except KeyError:
            raise HandlerNotFound.for_command(command)
