from src.entity_id import EntityId


class User:
    def __init__(self, id: EntityId, first_name: str, last_name: str, email: str) -> None:
        self._id = id
        self._first_name = first_name
        self._last_name = last_name
        self._email = email

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def full_name(self) -> str:
        return f"{self._first_name} {self._last_name}"

    @property
    def email(self) -> str:
        return self._email
