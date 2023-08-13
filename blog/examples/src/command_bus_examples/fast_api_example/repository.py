import copy
from abc import ABC, abstractmethod

from src.command_bus_examples.fast_api_example.entity_id import EntityId
from src.command_bus_examples.fast_api_example.errors import UserAlreadyExist, UserNotFound
from src.command_bus_examples.fast_api_example.user import User


class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: EntityId) -> User:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[EntityId, User] = {}

    def get(self, user_id: EntityId) -> User:
        try:
            return copy.deepcopy(self._users[user_id])
        except KeyError as error:
            raise UserNotFound(f"User with id={user_id} was not found!") from error

    def save(self, user: User) -> None:
        for existing_user in self._users.values():
            if existing_user.email == user.email:
                raise UserAlreadyExist(f"User with email={user.email} already exist!")

        self._users[user.id] = copy.deepcopy(user)
