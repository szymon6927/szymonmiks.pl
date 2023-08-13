from dataclasses import dataclass

from src.command_bus_examples.command import Command


@dataclass(frozen=True)
class RegisterUser(Command):
    email: str


@dataclass(frozen=True)
class NotRegisteredCommand(Command):
    pass


class RegisterUserHandler:
    def __call__(self, command: RegisterUser) -> None:
        print(f"Registering {command.email}")
