from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from dateutil.relativedelta import relativedelta


@dataclass(frozen=True)
class DateRange:
    start_date: datetime
    end_date: datetime

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("Can not create DateRange")

    def __composite_values__(self) -> Tuple[datetime, datetime]:
        return self.start_date, self.end_date

    @classmethod
    def one_week(cls) -> "DateRange":
        start_date = datetime.now()
        end_date = start_date + relativedelta(weeks=1)
        return cls(start_date, end_date)

    @classmethod
    def two_weeks(cls) -> "DateRange":
        start_date = datetime.now()
        end_date = start_date + relativedelta(weeks=2)
        return cls(start_date, end_date)

    @classmethod
    def one_month(cls) -> "DateRange":
        start_date = datetime.now()
        end_date = start_date + relativedelta(months=1)
        return cls(start_date, end_date)

    def is_within_range(self, date: datetime) -> bool:
        return self.start_date <= date <= self.end_date
