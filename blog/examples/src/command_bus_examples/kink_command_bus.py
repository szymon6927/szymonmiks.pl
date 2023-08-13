from dataclasses import dataclass
from typing import Type

from kink import Container
from kink.errors import ServiceError

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


class KinkCommandBus(CommandBus):
    def __init__(self, container: Container) -> None:
        self._container = container

    def register_handler(self, command: Type[Command], handler: HandlerType) -> None:
        if not issubclass(handler.__class__, Handler):
            raise ValueError("Handler must be a subclass of Handler[TCommand]")

        if command in self._container:
            raise CommandAlreadyRegistered.for_command(command.__name__)

        self._container[command] = handler

    def execute(self, command: Command) -> None:
        try:
            handler = self._container[type(command)]
            handler(command)
        except ServiceError as error:
            raise HandlerNotFound.for_command(command) from error
