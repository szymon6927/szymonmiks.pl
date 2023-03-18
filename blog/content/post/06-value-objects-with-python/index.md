+++
author = "Szymon Miks"
title = "Value objects with Python"
description = "Value objects explained with Python examples"
date = "2022-03-19"
image = "img/marketing-branding-creativity-business-values.jpeg"
categories = [
     "Python", "Software_Development", "DDD"
]
tags = [
    "python", "value objects", "DDD", "software development"
]
draft = false
+++

A **Value object** is a basic building block from tactical DDD (Domain Driven Design).

In today's blog post, I will show you how to build value objects with **Python** :snake:

## Definition

[As wikipedia says](https://en.wikipedia.org/wiki/Value_object):
> In computer science, a value object is a small object that represents a simple entity whose equality is not based on identity: i.e. two value objects are equal when they have the same value, not necessarily being the same object.

More detailed explanation can be found in those two books:
- [Domain-Driven Design: Tackling Complexity in the Heart of Software](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215/)
- [Implementing Domain-Driven Design](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)

I can’t recommend them enough :point_up: &nbsp;, especially the second one.


## Characteristics of a value object
- Describes the features of a specific domain concept
- Binds many attributes into a logical business concept
- Has no identity; it's identified by the values of the attributes
- Comparison is done through comparing values of the attributes
- It's immutable
- Has no methods that can change the object's state (if such a method is needed a new object should be returned instead)
- Side effect free behavior


## Benefits
- Built-in validation
- Internal implementation is easy to change because our object has a stable interface
- Encapsulates the logic, for example: validation
- Improves code readability
- Helps you fight with [Primitive Obsession](https://refactoring.guru/smells/primitive-obsession)
- Easy to unit test

## Examples

I decided to use [dataclasses](https://docs.python.org/3/library/dataclasses.html) in my examples due to the following reasons:
- `frozen=True` guarantees the object's immutability
- by default dataclasses are shipped with `__eq__()` method (`eq=True`) which enables objects comparison

Using pure python classes is possible but inefficient as you have to take care of the above by yourself.

Some examples in this blog post may be perceived as half-baked. The reason for that is the fact that
some of them are taken from my projects, and others written explicitly for the purpose of this blog post :sunglasses:.

All of them, together with unit tests are available on my
GitHub :rocket: - https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/src/value_object_example

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class Price:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Price can not be smaller than 0")

    @classmethod
    def zero(cls) -> "Price":
        return cls(Decimal(0))

    @classmethod
    def of(cls, value: Union[int, str, float]) -> "Price":
        return Price(Decimal(value))

    def discount(self, percentage: int) -> "Price":
        return Price(Decimal(percentage * self.value / 100))

    def __add__(self, other: "Price") -> "Price":
        return Price(self.value + other.value)

    def __sub__(self, other: "Price") -> "Price":
        return Price(self.value - other.value)

    def __mul__(self, other: "Price") -> "Price":
        return Price(self.value * other.value)

    def __str__(self) -> str:
        return f"{self.value:.2f}"

```

---

```python
import re
from dataclasses import dataclass
from email.utils import parseaddr
from typing import ClassVar


@dataclass(frozen=True)
class EmailAddress:
    value: str
    _trusted_domains: ClassVar[list[str]] = [
        "zut.edu.pl",
        "pg.edu.pl",
        "amsterdamumc.nl",
    ]  # can be much more here

    def __post_init__(self) -> None:
        real_name, email_address = parseaddr(self.value)

        if not real_name and not email_address:
            raise ValueError("Incorrect email address!")

        regex_result = re.search(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+",
            email_address,
        )
        if not regex_result:
            raise ValueError("Incorrect email address!")

    @classmethod
    def academical(cls, email_address: str) -> "EmailAddress":
        email = cls(email_address)
        domain = email.value.split("@")[1]

        if domain not in cls._trusted_domains:
            raise ValueError("Non-academical email address!")

        return email

    def change(self, new_email_address: str, is_academical: bool) -> "EmailAddress":
        if is_academical:
            return self.academical(new_email_address)

        return EmailAddress(new_email_address)

    def __str__(self) -> str:
        return self.value

```

---

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OpenSSHPublicKey:
    key: str

    def __post_init__(self):
        if "ssh-rsa" not in self.key:
            raise ValueError("Provided OpenSSH key has incorrect format!")

    def __str__(self) -> str:
        return self.key

```

---

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SSH2PublicKey:
    key: str

    def __post_init__(self) -> None:
        if not self.key.startswith(
            "---- BEGIN SSH2 PUBLIC KEY ----"
        ) and not self.key.endswith("---- END SSH2 PUBLIC KEY ----"):
            raise ValueError("Provided SSH2 public key has incorrect format!")

    def __str__(self) -> str:
        return self.key

```

---

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisParameters:
    has_cf_correction: bool
    has_batch_correction: bool

```

## Summary

I hope you enjoyed it :wink:

A value object is a great starting point to improve readability of your code and make it cleaner.
It's also an excellent technique if you struggle with refactorization, as it may fix the following issues:
- duplicated validation
- multiplied representation of the same concept
- a large `utils` file :smile:

I hope you see the benefits of using value objects after reading this blog post.
Please let me know, I would love to hear your opinion!
