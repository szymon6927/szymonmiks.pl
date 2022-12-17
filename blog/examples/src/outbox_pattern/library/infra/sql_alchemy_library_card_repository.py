from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import Session, composite, joinedload, registry, relationship

from src.outbox_pattern.library.domain.date_range import DateRange
from src.outbox_pattern.library.domain.library_card import LibraryCard, Status
from src.outbox_pattern.library.domain.library_card_repository import ILibraryCardRepository
from src.outbox_pattern.library.domain.rental import Rental
from src.outbox_pattern.shared.db import metadata
from src.outbox_pattern.shared.entity_id import EntityId

mapper_registry = registry(metadata=metadata)


library_card_table = Table(
    "library_cards",
    metadata,
    Column("id", CHAR(32), primary_key=True),
    Column("owner_id", CHAR(32), nullable=False),
    Column("status", String(20), nullable=False),
    Column("created_at", DateTime, nullable=False),
)

rental_table = Table(
    "rentals",
    metadata,
    Column("id", CHAR(32), primary_key=True),
    Column("library_card_id", CHAR(32), ForeignKey("library_cards.id"), nullable=False),
    Column("resource_id", CHAR(32), nullable=False),
    Column("rental_period_start_date", DateTime, nullable=False),
    Column("rental_period_end_date", DateTime, nullable=False),
)


mapper_registry.map_imperatively(
    LibraryCard,
    library_card_table,
    properties={
        "_id": composite(lambda value: EntityId.of(value), library_card_table.c.id),
        "__id": library_card_table.c.id,
        "_owner_id": composite(lambda value: EntityId.of(value), library_card_table.c.owner_id),
        "__owner_id": library_card_table.c.owner_id,
        "_rentals": relationship(Rental),
        "_status": composite(lambda value: Status(value), library_card_table.c.status),
        "__status": library_card_table.c.status,
    },
    column_prefix="_",
)

mapper_registry.map_imperatively(
    Rental,
    rental_table,
    properties={
        "_id": composite(lambda value: EntityId.of(value), rental_table.c.id),
        "__id": rental_table.c.id,
        "_resource_id": composite(lambda value: EntityId.of(value), rental_table.c.resource_id),
        "__resource_id": rental_table.c.resource_id,
        "_rental_period": composite(
            lambda start_date, end_date: DateRange(start_date=start_date, end_date=end_date),
            rental_table.c.rental_period_start_date,
            rental_table.c.rental_period_end_date,
        ),
    },
    column_prefix="_",
)


class SqlAlchemyLibraryCardRepository(ILibraryCardRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, library_card_id: EntityId) -> LibraryCard:
        result: LibraryCard = (
            self._session.query(LibraryCard).options(joinedload("*")).filter_by(_id=library_card_id).one()
        )
        result._domain_events = []
        return result

    def save(self, library_card: LibraryCard) -> None:
        self._session.merge(library_card)
        library_card.clear_domain_events()
