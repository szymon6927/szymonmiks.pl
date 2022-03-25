+++
author = "Szymon Miks"
title = "Value objects with Python"
description = "Value objects explained with Python code examples"
date = "2022-03-19"
image = "img/joshua-reddekopp-SyYmXSDnJ54-unsplash.jpeg"
categories = [
     "Python", "Software_Development"
]
tags = [
    "python", "value objects", "DDD", "software development"
]
draft = true
+++

**Value object** is basic building block from tactical DDD (Domain Driven Design).

In today's blog post, I will show you, how you can build value objects with **Python** :snake:

## Definition

[As wikipedia says](https://en.wikipedia.org/wiki/Value_object):
> In computer science, a value object is a small object that represents a simple entity whose equality is not based on identity: i.e. two value objects are equal when they have the same value, not necessarily being the same object.

The best explanation about it, you will find in these two books:
- [Domain-Driven Design: Tackling Complexity in the Heart of Software](https://www.amazon.com/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215/)
- [Implementing Domain-Driven Design](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)

I really recommend them :point_up: &nbsp;, especially the second one.


## Characteristics of value object
- describes the features of a specific domain concept
- binds many attributes into a logical business concept
- has no identity, it's identified by the values of the attributes
- comparison is done through comparing values of the attributes
- it's immutable
- has no methods that will change the object's state (if such method is needed new object should be returned)
- side effect free behavior


## Benefits
- builtin validation
- internal implementation is easy to change because we have the stable interface of our object
- encapsulates the logic, for example: validation
- improves code readability
- helps you fight with [Primitive Obsession](https://refactoring.guru/smells/primitive-obsession)
- easy to unit test

## Examples

Before we go to the examples. I decided to use [dataclasses](https://docs.python.org/3/library/dataclasses.html) due to:
- `frozen=True` guarantees the immutability
- `eq=True` is setup by default which means that `__eq__()` method will be generated automatically

You can use pure python classes, but then you have to take care of the above things by yourself.

Examples below, I decided to mix them. 
Some of them have been taken from my projects. 
Some of them have been figured out by myself for purpose of this blog post. :sunglasses:

All of them, together with unit tests are available on my GitHub <link here>.

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

I hope you enjoy it :wink:

A value object is a great starting point to make your code more clean and readable.
When it comes to refactorization - it's also an excellent technique if you struggle with:
- duplicated validation
- multiplied representation of the same concept
- too large `utils` file :smile: 

I hope you see the benefits of using value objects after reading this blog post. 
Please let me know, I would love to hear your opinion!
