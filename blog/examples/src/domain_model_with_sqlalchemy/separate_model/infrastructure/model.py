from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from src.domain_model_with_sqlalchemy.db import Base


class LibraryCardModel(Base):
    __tablename__ = "library_cards_separate_model"

    id = Column(CHAR(32), primary_key=True)
    owner_id = Column(CHAR(32), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
    rentals = relationship("RentalModel", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return (
            f"LibraryCardModel(id={self.id}, owner_id={self.owner_id}, "
            f"status={self.status}, created_at={self.created_at})"
        )


class RentalModel(Base):
    __tablename__ = "rentals_separate_model"

    id = Column(CHAR(32), primary_key=True)
    library_card_id = Column(CHAR(32), ForeignKey("library_cards_separate_model.id"), nullable=False)
    resource_id = Column(CHAR(32), nullable=False)
    rental_period_start_date = Column(DateTime, nullable=False)
    rental_period_end_date = Column(DateTime, nullable=False)

    def __str__(self) -> str:
        return (
            f"RentalModel(id={self.id}, library_card_id={self.library_card_id}, resource_id={self.resource_id}, "
            f"rental_period_start_date={self.rental_period_start_date}, "
            f"rental_period_end_date={self.rental_period_end_date})"
        )
