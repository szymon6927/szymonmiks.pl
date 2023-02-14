from dataclasses import dataclass

from dateutil.relativedelta import relativedelta

from src.domain_model_with_sqlalchemy.separate_model.domain.date_range import DateRange
from src.domain_model_with_sqlalchemy.separate_model.domain.entity_id import EntityId


@dataclass
class Rental:
    _id: EntityId
    _resource_id: EntityId
    _rental_period: DateRange

    @classmethod
    def create(cls, resource_id: EntityId, rental_period: DateRange) -> "Rental":
        return cls(_id=EntityId.new_one(), _resource_id=resource_id, _rental_period=rental_period)

    @property
    def id(self) -> EntityId:
        return self._id

    @property
    def resource_id(self) -> EntityId:
        return self._resource_id

    @property
    def rental_period(self) -> DateRange:
        return self._rental_period

    def prolong(self, days: int) -> None:
        if days > 7:
            raise ValueError("7 days is the maximum prolongation period!")

        self._rental_period = DateRange(
            self._rental_period.start_date, self._rental_period.end_date + relativedelta(days=days)
        )
