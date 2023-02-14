from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Db:
    def __init__(self, connection_url: str) -> None:
        self._engine = create_engine(connection_url, future=True, echo=True)
        metadata.create_all(bind=self._engine)

    @property
    def session(self) -> Session:
        session_factory = sessionmaker(bind=self._engine, future=True)
        return session_factory()
