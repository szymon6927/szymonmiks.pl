from email_validator import EmailNotValidError, validate_email

from src.command_bus_examples.fast_api_example.commands import RegisterUser
from src.command_bus_examples.fast_api_example.errors import ValidationError
from src.command_bus_examples.fast_api_example.repository import UserRepository
from src.command_bus_examples.fast_api_example.user import User
from src.command_bus_examples.generic_handler import Handler


class RegisterUserHandler(Handler[RegisterUser]):
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def __call__(self, command: RegisterUser) -> None:
        try:
            validated_email = validate_email(command.email, check_deliverability=False)

            self._user_repository.save(User(command.id, command.first_name, command.last_name, validated_email.email))
        except EmailNotValidError as error:
            raise ValidationError(f"Provided email value `{command.email}` is not correct") from error
