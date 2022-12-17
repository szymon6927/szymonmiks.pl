import copy
import uuid
from datetime import datetime
from enum import Enum, unique
from typing import Tuple

from src.outbox_pattern.library.domain.date_range import DateRange
from src.outbox_pattern.library.domain.errors import BorrowingError
from src.outbox_pattern.library.domain.events import (
    ItemProlonged,
    ItemRented,
    ItemReturned,
    LibraryCardCreated,
    LibraryCardSuspended,
)
from src.outbox_pattern.library.domain.rental import Rental
from src.outbox_pattern.shared.entity_id import EntityId
from src.outbox_pattern.shared.errors import ResourceNotFound
from src.outbox_pattern.shared.event import Event


@unique
class Status(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

    def __composite_values__(self) -> Tuple[str]:
        return (self.value,)


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
        self._domain_events: list[Event] = []

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def events(self) -> list[Event]:
        return self._domain_events[:]

    @classmethod
    def create(cls, owner_id: EntityId) -> "LibraryCard":
        instance = cls(id=EntityId.new_one(), owner_id=owner_id, rentals=[], status=Status.ACTIVE)
        instance._add_domain_event(
            LibraryCardCreated(
                id=uuid.uuid4().hex,
                occurred_on=datetime.utcnow(),
                card_id=str(instance.id),
                owner_id=str(instance._owner_id),
            )
        )
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
        self._add_domain_event(
            ItemRented(
                id=uuid.uuid4().hex,
                occurred_on=datetime.utcnow(),
                resource_id=str(resource_id),
                starts_at=how_long.start_date,
                ends_at=how_long.end_date,
            )
        )

    def prolong_for(self, rental_id: EntityId, days: int) -> None:
        rental = next((rental for rental in self._rentals if rental.id == rental_id), None)

        if not rental:
            raise ResourceNotFound

        rental.prolong(days)

        self._add_domain_event(
            ItemProlonged(
                id=uuid.uuid4().hex,
                occurred_on=datetime.utcnow(),
                resource_id=str(rental.resource_id),
                prolonged_for=days,
                starts_at=rental.rental_period.start_date,
                ends_at=rental.rental_period.end_date,
            )
        )

    def give_back(self, resource_id: EntityId) -> None:
        rental = next((rental for rental in self._rentals if rental.resource_id == resource_id), None)

        if not rental:
            raise ResourceNotFound

        self._rentals.remove(rental)
        self._add_domain_event(
            ItemReturned(id=uuid.uuid4().hex, occurred_on=datetime.utcnow(), resource_id=str(resource_id))
        )

        days_diff = (datetime.utcnow() - rental.rental_period.end_date).days
        if days_diff > 3:
            self._add_domain_event(
                LibraryCardSuspended(
                    id=uuid.uuid4().hex,
                    occurred_on=datetime.utcnow(),
                    card_id=str(self._id),
                    owner_id=str(self._owner_id),
                )
            )
            self._status = Status.SUSPENDED

    def is_active(self) -> bool:
        return self._status == Status.ACTIVE

    def is_owned_by(self, owner: EntityId) -> bool:
        return self._owner_id == owner

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def _add_domain_event(self, event: Event) -> None:
        self._domain_events.append(event)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LibraryCard):
            raise AttributeError()

        vars_copy = copy.deepcopy(vars(self))
        other_vars_copy = copy.deepcopy(vars(other))

        attrs_to_remove = [attr for attr in vars_copy.keys() if attr.startswith("_sa_")]
        for attr in attrs_to_remove:
            del vars_copy[attr]
            del other_vars_copy[attr]

        return vars_copy == other_vars_copy

    def __str__(self) -> str:
        return f"LibraryCard(id={self._id}), owner_by={self._owner_id}, rentals={self._rentals}, status={self._status}"
