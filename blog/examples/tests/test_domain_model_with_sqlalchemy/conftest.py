from typing import Iterator

import pytest
from sqlalchemy.orm import Session

from src.domain_model_with_sqlalchemy.db import Db


@pytest.fixture()
def db() -> Db:
    # db_url = "sqlite:///db.sqlite"
    db_url = "sqlite://"
    db = Db(db_url)
    return db


@pytest.fixture()
def session(db: Db) -> Iterator[Session]:
    session = db.session
    yield session
    session.close()
