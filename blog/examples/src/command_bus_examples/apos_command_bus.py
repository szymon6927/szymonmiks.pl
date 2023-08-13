from typing import Type

from apos import Apos, MissingHandler, OverwritingHandler

from src.command_bus_examples.command import Command
from src.command_bus_examples.command_bus import CommandBus
from src.command_bus_examples.custom_types import HandlerType
from src.command_bus_examples.errors import CommandAlreadyRegistered, HandlerNotFound


class AposCommandBus(CommandBus):
    def __init__(self) -> None:
        self._apos = Apos()

    def register_handler(self, command: Type, handler: HandlerType) -> None:
        try:
            self._apos.subscribe_command(command, handler)
        except OverwritingHandler as error:
            raise CommandAlreadyRegistered.for_command(command.__name__) from error

    def execute(self, command: Command) -> None:
        try:
            self._apos.publish_command(command)
        except MissingHandler as error:
            raise HandlerNotFound.for_command(command) from error
