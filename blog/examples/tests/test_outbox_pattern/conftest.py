from dataclasses import dataclass
from typing import Iterator

import pytest
from sqlalchemy.orm import Session

from src.outbox_pattern.shared.db import Db
from src.outbox_pattern.shared.event import Event


@pytest.fixture()
def db() -> Db:
    db_url = "sqlite://"
    db = Db(db_url)
    return db


@pytest.fixture()
def session(db: Db) -> Iterator[Session]:
    session = db.session
    yield session
    session.close()


@dataclass(frozen=True)
class SomethingImportantHappened(Event):
    message: str
