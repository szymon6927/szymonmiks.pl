+++
author = "Szymon Miks"
title = "Basic Building Blocks DDD - Entities"
description = "How to implement DDD Entities in Python"
date = "2023-12-21"
image = "img/ryan-quintal-US9Tc9pKNBU-unsplash.jpg"
categories = [
     "Python", "Software_Development", "DDD"
]
tags = [
    "python",
    "entities",
    "entity",
    "DDD",
    "domain driven design",
    "domain-driven-design",
    "software development"
]
draft = false
+++

## Intro

Some time ago I created a blog post about "[Value Objects](/p/value-objects-with-python/)".
I want to continue the series about DDD tactic building blocks and in
today's blog post I want to show you another building block - **entity**.

## What is an entity?

> Entity - an identifiable object that contains and encapsulates business logic

This is the simplest and shortest definition I can think of regarding entity.

If we would want to take a deeper look at what it means. It means that the entity is
a building block that is used to describe the structure of our model. By **model**, I mean the technical
solution/implementation for a problem that exists in the real world/business.

It means that an entity is something that:
- changes over time (it is mutable)
- has life cycle
- has an identity that is different from the value of attributes that describe it

For example, if we want to model a citizen of some country, we could define an entity `Citizen`.
This citizen may have some attributes like: first name, last name, height, marital status, or eye color.
Even if our citizen will decide to change their first name, last name, or marital status.
It is still the same citizen.

To be able to identify the citizen we have to endow him identity.
This identity may be the personal identity number.

Our citizen obtains their personal identity number sometime after birth.
Years later, the first name, last name, or height may be different.
Even the color of the eyes may change, and he may have some diseases.
It is still the same citizen. His attributes have changed over time but his identity is the same.

For these types of things that we find during our domain modeling, we will want
to describe/define them using **entities**.

## Implementation

Entity is a mutable object, we have to make sure that the change will be done safely.
What does `safely` in the context mean? It means that we want to perform the change
ensuring all business rules.

Our entity exposes methods (behaviors) named in a domain language that encapsulates all the implementation details like state checks, validation, etc.
No public getters and setters.
We don't want to allow anyone outside our module to manipulate any attribute of our entity.

In simple words, the procedure is as follows:
- public method names using domain language
- perform business logic, check all the rules, invariants, etc
- change the state of the entity

Let me show you the code example from one of my projects. I will obfuscate the business domain to not break the NDA.
Let's imagine that you have some sort of analytical report.
A client can suppress some of the items from the analytical report.
Based on it, you want to show some metrics to the client.
By default, if there are no suppressed data items all metrics are equal to 0.
The client may suppress up to 10 data items.
Once he requests the metrics taking into account the suppressed data items the recalculation needs to happen.
The client may disable the suppression whenever he wants.

```python
from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from typing import List
from enum import Enum, unique
from decimal import Decimal
import random

@dataclass(frozen=True)
class SuppressionId:
    value: UUID


@dataclass(frozen=True)
class DataItem:
    name: str
    value: Decimal

    def __post_init__(self) -> None:
        if " " in self.name:
            raise ValueError(
                f"The provided data item name `{self.name}` is not correct."
            )


@unique
class SuppressionStatus(Enum):
    ACTIVATED = "activated"
    DISABLED = "disabled"


@dataclass(frozen=True)
class Metrics:
    metric_a: Decimal = Decimal(0)
    metric_b: Decimal = Decimal(0)
    metric_c: Decimal = Decimal(0)
    metric_d: Decimal = Decimal(0)


class SuppressionError(Exception):
    pass


class Suppression:
    DATA_ITEMS_SUPPRESSION_LIMIT = 10

    def __init__(self, id: SuppressionId, owner: str) -> None:
        self._id = id
        self._owner = owner
        self._data_items: List[DataItem] = []
        self._metrics = Metrics()
        self._status = SuppressionStatus.ACTIVATED

    @property
    def id(self) -> SuppressionId:
        return self._id

    @property
    def data_items(self) -> List[DataItem]:
        return self._data_items

    @property
    def metrics(self) -> Metrics:
        return self._metrics

    @property
    def is_active(self) -> bool:
        return self._status == SuppressionStatus.ACTIVATED

    def disable(self) -> None:
        self._status = SuppressionStatus.DISABLED

    def activate(self) -> None:
        self._status = SuppressionStatus.ACTIVATED

    def suppress_data_item(self, data_item: DataItem) -> None:
        if len(self._data_items) == self.DATA_ITEMS_SUPPRESSION_LIMIT:
            raise SuppressionError(
                f"`You can suppress only up to `{self.DATA_ITEMS_SUPPRESSION_LIMIT}` data items"
            )

        if self._status == SuppressionStatus.DISABLED:
            raise SuppressionError(
                "Can not perform any changes on a `Suppression` that is disabled"
            )

        if data_item in self._data_items:
            return

        self._data_items.append(data_item)

    def restore_data_item(self, data_item: DataItem) -> None:
        if self._status == SuppressionStatus.DISABLED:
            raise SuppressionError(
                "Can not perform any changes on a `Suppression` that is disabled"
            )

        try:
            self._data_items.remove(data_item)
        except ValueError:
            return

    def recalculate_metrics(self) -> Metrics:
        if self._status == SuppressionStatus.DISABLED:
            raise SuppressionError(
                "Can not recalculate metrics on a disabled `Suppression`"
            )

        if len(self._data_items) == 0:
            return Metrics()

        return self._recalculate_metrics()

    def _recalculate_metrics(self) -> Metrics:
        # math operations needed for metrics recalculation
        # skipping this part of the code as it is implementation details
        # and does not bring any value to the example I want to show you
        return Metrics(
            Decimal(random.randrange(0, 1000)),
            Decimal(random.randrange(0, 1000)),
            Decimal(random.randrange(0, 1000)),
            Decimal(random.randrange(0, 1000))
        )
```



## God entity

One of the problems I consider most dangerous is the "God entity class".

> God class, or god object is a class that does too much.

Have you ever seen things like `class User` or `class Order` in your project?

Where literally everything is inside it? User details, user permissions, user roles, user activities.
When it comes to `Order` - order details, order items, invoice details, payment details, statuses, and sub-statuses.

Let's be fair, modeling an entity is not about it. We should consider it as an anti-pattern.
Trust me from a long-time perspective maintaining such software is almost impossible. The complexity grows exponentially

Refactor it as soon as possible.
I realize that refactoring such a class is not easy.
Let me know if you would like to see another blog post that will be exactly about it.
I can show you some patterns/heuristics on how to deal with such problems.


## Summary

In this exploration of Domain-Driven Design (DDD), we delved into the foundational concept of entities, crucial components that encapsulate the core business logic of an application.

Entities stand as the bedrock upon which rich domain models are built.
They serve as more than just data structures, evolving into active participants in the business processes, embodying the true essence of DDD principles.

That’s all Folks!
Thank you for staying till the end.
We lay the groundwork for future discussions.
I plan to write about other building blocks too like repositories, aggregated, and factories.

Stay tuned and happy coding!
