from rocketry import Rocketry
from rocketry.conditions.api import every

from src.outbox_pattern import messenger
from src.outbox_pattern.outbox.outbox_processor import OutboxProcessor
from src.outbox_pattern.outbox.sql_alchemy_message_outbox import SqlAlchemyMessageOutbox
from src.outbox_pattern.shared.db import Db

app = Rocketry()


@app.task(every("10 seconds"))
def process_messages() -> None:
    session = Db("sqlite:///db.sqlite").session
    message_outbox = SqlAlchemyMessageOutbox(session)
    processor = OutboxProcessor(message_outbox, session, messenger)

    processor.process_outbox_message()


if __name__ == "__main__":
    app.run()
