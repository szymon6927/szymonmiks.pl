from dataclasses import dataclass

from src.command_bus_examples.command import Command
from src.entity_id import EntityId


@dataclass(frozen=True)
class RegisterUser(Command):
    id: EntityId
    first_name: str
    last_name: str
    email: str
