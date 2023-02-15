from datetime import datetime

from src.domain_model_with_sqlalchemy.errors import BorrowingError, ResourceNotFound
from src.domain_model_with_sqlalchemy.separate_model.domain.date_range import DateRange
from src.domain_model_with_sqlalchemy.separate_model.domain.entity_id import EntityId
from src.domain_model_with_sqlalchemy.separate_model.domain.rental import Rental
from src.domain_model_with_sqlalchemy.separate_model.domain.status import Status


class LibraryCard:
    def __init__(
        self,
        id: EntityId,
        owner_id: EntityId,
        rentals: list[Rental],
        status: Status,
        created_at: datetime = datetime.utcnow(),
    ) -> None:
        self._id = id
        self._owner_id = owner_id
        self._rentals = rentals
        self._status = status
        self._created_at = created_at

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def owner_id(self) -> EntityId:
        return self._owner_id

    @property
    def rentals(self) -> list[Rental]:
        return self._rentals

    @property
    def status(self) -> Status:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @classmethod
    def create(cls, owner_id: EntityId) -> "LibraryCard":
        instance = cls(id=EntityId.new_one(), owner_id=owner_id, rentals=[], status=Status.ACTIVE)
        return instance

    def borrow(self, resource_id: EntityId, how_long: DateRange) -> None:
        if not self.is_active():
            raise BorrowingError("Can not borrow")

        days_diff = (how_long.end_date - how_long.start_date).days
        if days_diff > 14:
            raise BorrowingError("You cannot borrow for more than 14 days at once!")

        if len(self._rentals) >= 3:
            raise BorrowingError("You can only have 3 resources borrowed!")

        rental = Rental.create(resource_id, how_long)
        self._rentals.append(rental)

    def prolong_for(self, rental_id: EntityId, days: int) -> None:
        rental = next((rental for rental in self._rentals if rental.id == rental_id), None)

        if not rental:
            raise ResourceNotFound(str(rental_id))

        rental.prolong(days)

    def give_back(self, resource_id: EntityId) -> None:
        rental = next((rental for rental in self._rentals if rental.resource_id == resource_id), None)

        if not rental:
            raise ResourceNotFound(str(resource_id))

        self._rentals.remove(rental)

        days_diff = (datetime.utcnow() - rental.rental_period.end_date).days
        if days_diff > 3:
            self._status = Status.SUSPENDED

    def is_active(self) -> bool:
        return self._status == Status.ACTIVE

    def is_owned_by(self, owner: EntityId) -> bool:
        return self._owner_id == owner

    def __str__(self) -> str:
        return f"LibraryCard(id={self._id}, owner_by={self._owner_id}, rentals={self._rentals}, status={self._status})"
