+++
author = "Szymon Miks"
title = "Domain model with SQLAlchemy"
description = "Different ways of persistence of our domain models"
date = "2023-01-14"
image = "img/campaign-creators-IKHvOlZFCOg-unsplash.jpg"
categories = [
     "Python", "Software_Development", "Architecture"
]
tags = [
    "python",
    "software development",
    "architecture",
    "domain model",
    "design patterns",
    "P of EAA",
    "persistence",
]
draft = false
+++

## Intro

Welcome to the world of databases and domain modelling!

In this blog post, we will explore the power of [SQLAlchemy](https://www.sqlalchemy.org/), a popular ORM library in Python, to model our domain objects.

We will look at how to define our entities, and how to persist them into a relational database.

Whether you're a beginner or an experienced Python developer, this post will provide you with the knowledge and skills you need to build robust, scalable, and maintainable domain models with SQLAlchemy.

So, let's dive in and see how we can bring our domains to life!


## Domain model

Before we jump straight into the code let's define what the domain model is, so we are on the same page.

**Domain Model** is a representation of the concepts and relationships that exist in a particular business or problem domain.

[According to Fowler](https://martinfowler.com/eaaCatalog/domainModel.html), a domain model is an object-oriented model that **encapsulates the behaviour and data** of the objects in the domain, and provides a clear and concise representation of the problem being solved.

The purpose of a domain model is to provide a **common language and understanding of the problem domain**, between the developers and stakeholders.
A well-designed domain model helps to bridge the gap between the **technical and business perspectives**, and provides a clear and concise representation of the system's requirements and behaviour.

The domain model highlights the importance of focusing on the **behaviour and interactions** of the objects in the domain, rather than on the **implementation details**.

## Ways of persisting domain models

I will use the domain model from one of the previous posts. This is a simple representation of a library card.

This class is a good candidate.
It is complex enough.
It has some related objects and quite a lot of value objects.
Only business methods are exposed, and implementation details are hidden.

Our goal is simple: **save the object to the database, but the object itself should know nothing about the database**.

The code is also available on my GitHub [here](https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/src/domain_model_with_sqlalchemy) :rocket:.

### Imperative mapping

SQLAlchemy comes with a nice feature called **"[Imperative mapping](https://docs.sqlalchemy.org/en/14/orm/mapping_styles.html#imperative-mapping)".**

Imperative mapping in SQLAlchemy is a technique for defining the relationship between database tables and Python classes using imperative code, rather than declarative code.
This involves creating a set of mappings that describe the relationships between tables, columns, and classes, and using this mapping to perform database operations.
Imperative mapping provides more flexibility than declarative mapping, but requires more manual setup and can be more verbose.

This is how our `repository` looks using this technique

```python
# blog/examples/src/domain_model_with_sqlalchemy/imperative_mapping/infrastructure/sql_alchemy_library_card_repository.py

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

```

And the entity itself:

```python
# blog/examples/src/domain_model_with_sqlalchemy/imperative_mapping/domain/library_card.py

from datetime import datetime

from src.domain_model_with_sqlalchemy.errors import BorrowingError, ResourceNotFound
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.date_range import DateRange
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.entity_id import EntityId
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.rental import Rental
from src.domain_model_with_sqlalchemy.imperative_mapping.domain.status import Status


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

```

As you can see on the first listing we defined the tables and the mapping.

The entity itself is not aware of anything related to the database!

The only thing that is needed and comes directly from SQLAlchemy is `__composite_values__` and this is needed to persist value objects.

Before I show you the code example, let me try to explain what `__composite_values__` is :wink:.

In SQLAlchemy, `__composite_values__` is a special method that can be defined on a custom composite type class to define how instances of the composite type are serialized and deserialized.

A composite type is a custom data type that can be used to represent a group of related values as a single unit.
For example, a composite type could be used to represent a physical address as a combination of street, city, state, and zip code.
In our case we use it to represent `EntityId` or `DateRange`.

When you define a composite type in SQLAlchemy, you can define the attributes of the composite type and its data types, and you can also define various methods and properties on the class to customize its behaviour.

It is a method that should return a tuple of values which represents the attributes of the composite type.
When an instance of the composite type is serialized (when it is written to a database), SQLAlchemy calls the `__composite_values__` method to obtain the values that should be stored.
When an instance of the composite type is deserialized (when it is read from a database), SQLAlchemy calls the constructor of the composite type with the tuple of values obtained from `__composite_values__`.

You can read more about it [here](https://docs.sqlalchemy.org/en/14/orm/composites.html).

The use case looks like that:

```python
# blog/examples/src/domain_model_with_sqlalchemy/imperative_mapping/domain/date_range.py

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

from dateutil.relativedelta import relativedelta


@dataclass(frozen=True)
class DateRange:
    start_date: datetime
    end_date: datetime

    def __composite_values__(self) -> Tuple[datetime, datetime]:
        return self.start_date, self.end_date

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("Can not create DateRange")

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
```



### Separate model

Another technique, I like to call "separate model". The idea is to create SQLAlchemy models and map them manually
onto the entity, on the repository level.

```python
# blog/examples/src/domain_model_with_sqlalchemy/separate_model/infrastructure/sql_alchemy_library_card_repository.py

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

```

Then we have a separate file where we define our SQLAlchemy models.

```python
# blog/examples/src/domain_model_with_sqlalchemy/separate_model/infrastructure/model.py

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
```

When it comes to our entity, we only had to add public `getters` to be able to map all properties to our SQLAlchemy model.
The rest stays the same.

```python
# blog/examples/src/domain_model_with_sqlalchemy/separate_model/domain/library_card.py

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

```

Again the entity itself is not aware of anything related to the database!

## Summary

We discussed how to use SQLAlchemy to persist domain models to the database.

We started by introducing the concept of a domain model and explaining why it's important to separate domain logic from persistence logic.

Then we discussed different ways of persisting domain models with SQLAlchemy.

Code examples for each of these approaches demonstrated how to define domain models and how to persist them to a database using SQLAlchemy.
They also discussed the pros and cons of each approach.

The techniques we discussed can be used to implement architecture patterns like Domain-Driven Design (DDD) and hexagonal architecture.
By separating domain logic from persistence logic, you can create more modular and maintainable systems that are easier to test and evolve over time.
SQLAlchemy provides a powerful toolkit for building domain models and persisting them to a database, allowing you to choose the right approach for your specific use case and architecture.

I hope you enjoyed it.

Let me know, how you approach the domain model and persistence. Which technique do you use? I would love to hear your opinion :wink:.
