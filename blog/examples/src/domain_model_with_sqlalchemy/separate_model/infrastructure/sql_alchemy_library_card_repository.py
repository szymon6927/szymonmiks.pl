from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload

from src.domain_model_with_sqlalchemy.errors import ResourceNotFound
from src.domain_model_with_sqlalchemy.separate_model.domain.date_range import DateRange
from src.domain_model_with_sqlalchemy.separate_model.domain.entity_id import EntityId
from src.domain_model_with_sqlalchemy.separate_model.domain.library_card import LibraryCard
from src.domain_model_with_sqlalchemy.separate_model.domain.library_card_repository import ILibraryCardRepository
from src.domain_model_with_sqlalchemy.separate_model.domain.rental import Rental
from src.domain_model_with_sqlalchemy.separate_model.domain.status import Status
from src.domain_model_with_sqlalchemy.separate_model.infrastructure.model import LibraryCardModel, RentalModel


class SqlAlchemyLibraryCardRepository(ILibraryCardRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_model(self, library_card: LibraryCard) -> LibraryCardModel:
        rentals = [
            RentalModel(
                id=str(rental.id),
                library_card_id=str(library_card.id),
                resource_id=str(rental.resource_id),
                rental_period_start_date=rental.rental_period.start_date,
                rental_period_end_date=rental.rental_period.end_date,
            )
            for rental in library_card.rentals
        ]

        return LibraryCardModel(
            id=str(library_card.id),
            owner_id=str(library_card.owner_id),
            status=library_card.status.value,
            created_at=library_card.created_at,
            rentals=rentals,
        )

    def get(self, library_card_id: EntityId) -> LibraryCard:
        try:
            result: LibraryCardModel = (
                self._session.query(LibraryCardModel).options(joinedload("*")).filter_by(id=str(library_card_id)).one()
            )
        except NoResultFound as error:
            raise ResourceNotFound(str(library_card_id)) from error

        rentals = [
            Rental(
                _id=EntityId.of(rental_model.id),
                _resource_id=EntityId.of(rental_model.resource_id),
                _rental_period=DateRange(
                    start_date=rental_model.rental_period_start_date, end_date=rental_model.rental_period_end_date
                ),
            )
            for rental_model in result.rentals
        ]

        return LibraryCard(
            id=EntityId.of(result.id),
            owner_id=EntityId.of(result.owner_id),
            rentals=rentals,
            status=Status(result.status),
            created_at=result.created_at,
        )

    def save(self, library_card: LibraryCard) -> None:
        model = self._to_model(library_card)
        self._session.merge(model)
