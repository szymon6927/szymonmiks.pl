from src.command_bus_examples.command_bus import CommandBus
from src.command_bus_examples.command_bus_using_generics import CommandBusUsingGenerics
from src.command_bus_examples.fast_api_example.command_handlers import RegisterUserHandler
from src.command_bus_examples.fast_api_example.commands import RegisterUser
from src.command_bus_examples.fast_api_example.repository import InMemoryUserRepository, UserRepository

command_bus = CommandBusUsingGenerics()
user_repository = InMemoryUserRepository()
command_bus.register_handler(RegisterUser, RegisterUserHandler(user_repository))


def get_command_bus() -> CommandBus:
    return command_bus


def get_user_repository() -> UserRepository:
    return user_repository
