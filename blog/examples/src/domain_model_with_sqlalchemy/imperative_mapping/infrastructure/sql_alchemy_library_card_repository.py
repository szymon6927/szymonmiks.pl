from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, composite, joinedload, relationship

from src.domain_model_with_sqlalchemy.db import mapper_registry, metadata
from src.domain_model_with_sqlalchemy.errors import ResourceNotFound
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.date_range import DateRange
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.entity_id import EntityId
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.library_card import LibraryCard
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.library_card_repository import ILibraryCardRepository
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.rental import Rental
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.status import Status


def init_mappers() -> None:
    library_card_table = Table(
        "library_cards_imperative_mapping",
        metadata,
        Column("id", CHAR(32), primary_key=True),
        Column("owner_id", CHAR(32), nullable=False),
        Column("status", String(20), nullable=False),
        Column("created_at", DateTime, nullable=False),
    )

    rental_table = Table(
        "rentals_imperative_mapping",
        metadata,
        Column("id", CHAR(32), primary_key=True),
        Column("library_card_id", CHAR(32), ForeignKey("library_cards_imperative_mapping.id"), nullable=False),
        Column("resource_id", CHAR(32), nullable=False),
        Column("rental_period_start_date", DateTime, nullable=False),
        Column("rental_period_end_date", DateTime, nullable=False),
    )

    mapper_registry.map_imperatively(
        LibraryCard,
        library_card_table,
        properties={
            "_id": composite(EntityId.of, library_card_table.c.id),
            "__id": library_card_table.c.id,
            "_owner_id": composite(lambda value: EntityId.of(value), library_card_table.c.owner_id),
            "__owner_id": library_card_table.c.owner_id,
            "_rentals": relationship(Rental, cascade="all, delete-orphan"),
            "_status": composite(Status, library_card_table.c.status),
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
        try:
            result: LibraryCard = (
                self._session.query(LibraryCard).options(joinedload("*")).filter_by(_id=library_card_id).one()
            )
            return result
        except NoResultFound as error:
            raise ResourceNotFound(str(library_card_id)) from error

    def save(self, library_card: LibraryCard) -> None:
        self._session.merge(library_card)
