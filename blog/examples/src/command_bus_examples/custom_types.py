from typing import Any, Callable, Union

from src.command_bus_examples.command import Command
from src.command_bus_examples.generic_handler import Handler

HandlerType = Union[Callable[[Any], None], Handler[Command]]
