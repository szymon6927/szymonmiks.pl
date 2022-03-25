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
