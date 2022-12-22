+++
author = "Szymon Miks"
title = "The outbox pattern in Python"
description = "Transactional Outbox pattern explained with Python examples."
date = "2022-12-17"
image = "img/siora-photography-gClIPKFrRjE-unsplash.jpg"
categories = [
     "Python", "Software_Development", "Architecture"
]
tags = [
    "python",
    "software development",
    "architecture",
    "outbox",
    "outbox pattern",
    "transactional outbox"
]
draft = false
mermaid = true
+++

## Intro

One of the most frequently used ways of communication between microservices/modules is asynchronous communications via events.

Implementing robust messaging might be challenging at times.
In today’s article, I will present you with how to implement the **outbox pattern** to guarantee the delivery of events and reliable messaging.

## The problem

{{<mermaid>}}
sequenceDiagram
    Application Service->>+Database: Begin transaction
    Application Service ->>+ Application Service: Execute business operation
    Application Service ->>+ Database: Save entity
    Application Service ->>+ Database: Commit transaction
    Application Service ->>+ EventBus: Send events
{{</mermaid>}}

---

The above diagram shows that after the end of the transaction we can’t guarantee that events will be delivered.

The problem is also presented in the following code. Please pay attention to line 14.

```python
class LibraryCardService:
    def __init__(
        self,
        library_card_repository: ILibraryCardRepository,
        event_bus: IEventBus
    ) -> None:
        self._library_card_repository = library_card_repository
        self._event_bus = event_bus

    def create(self, owner_id: str) -> LibraryCard:
        library_card = LibraryCard.create(EntityId.of(owner_id))
        events = library_card.events
        self._library_card_repository.save(library_card)
        # end of transaction

        for event in events:
            self._event_bus.publish(event)

        return library_card

```

This clearly shows that delivery of the events is not guaranteed. The reasons for this might be the following:
- our system may go down just after the "commit" operation
- there can be something wrong with our event bus

## The outbox pattern

The outbox pattern (transactional outbox or store and forward event publisher) is the solution.

We want to ensure that our business entities and our business events are stored within the same transaction.

---

{{<mermaid>}}
sequenceDiagram
    Application Service->>+Database: Begin transaction
    Application Service ->>+ Application Service: Execute business operation
    Application Service ->>+ Database: Save entity
    Application Service ->>+ Database: Save events to outbox
    Application Service ->>+ Database: Commit transaction
{{</mermaid>}}

---

Later on, a periodic task (e.g. CRON job) can process the previously saved events.

---

{{<mermaid>}}
sequenceDiagram
    MessageOutbox->>+Database: Get unprocessed events
    Database ->>+ MessageOutbox: Events to process
    MessageOutbox ->>+ EventBus: Send events
    MessageOutbox ->>+ Database: Mark events as processed
{{</mermaid>}}

---

This approach gives us **"at least once delivery"**.

It is worth noting that **"at least once delivery"** means that the same events might be delivered multiple times.
We should keep this in mind and endeavor to create event handlers that are idempotent.

Ok, that’s enough about theory.
Let's not go deeply into the theoretical side of it (there are already enough of such articles on the web).
Instead, let's focus on a more practical approach.

## Example

The full code example, you can find it together with tests on my GitHub :rocket:.

https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/src/outbox_pattern

The application service:

```python
# blog/examples/src/outbox_pattern/library/application/service.py

class LibraryCardService:
    def __init__(
        self,
        library_card_repository: ILibraryCardRepository,
        event_bus: IEventBus,
        session: Session
    ) -> None:
        self._library_card_repository = library_card_repository
        self._event_bus = event_bus
        self._session = session

    def create(self, owner_id: str) -> LibraryCard:
        library_card = LibraryCard.create(EntityId.of(owner_id))

        with self._session.begin():
            events = library_card.events
            self._library_card_repository.save(library_card)

            for event in events:
                self._event_bus.publish(event)

        return library_card

```

As you can see, we save the entity and events within the same transaction.

The `events` property of our business object returns the list of events that need to be published:

```python
# blog/examples/src/outbox_pattern/library/domain/library_card.py

class LibraryCard:
    ...

    @property
    def events(self) -> list[Event]:
        return self._domain_events[:]

    @classmethod
    def create(cls, owner_id: EntityId) -> "LibraryCard":
        instance = cls(
            id=EntityId.new_one(),
            owner_id=owner_id,
            rentals=[],
            status=Status.ACTIVE
        )
        instance._add_domain_event(
            LibraryCardCreated(
                id=uuid.uuid4().hex,
                occurred_on=datetime.utcnow(),
                card_id=str(instance.id),
                owner_id=str(instance._owner_id),
            )
        )
        return instance

    def _add_domain_event(self, event: Event) -> None:
        self._domain_events.append(event)

    ...
```

The events are simple python dataclasses that are immutable.

```python
# blog/examples/src/outbox_pattern/library/domain/events.py

@dataclass(frozen=True)
class Event:
    id: str
    occurred_on: datetime


@dataclass(frozen=True)
class LibraryCardCreated(Event):
    card_id: str
    owner_id: str

```

The `OutboxMessage` definition:

```python
# blog/examples/src/outbox_pattern/outbox/message.py

@dataclass(frozen=True)
class MessageType:
    qualified_name: str

    def module_name(self) -> str:
        without_class_name = self.qualified_name.split(".")[:-1]
        return ".".join(without_class_name)

    def class_name(self) -> str:
        return self.qualified_name.split(".")[-1]

    def __str__(self) -> str:
        return self.qualified_name


@dataclass
class OutboxMessage:
    id: EntityId
    occurred_on: datetime
    type: MessageType
    data: dict[str, Any]
    processed_on: Optional[datetime]

```

Ok, now we can move to the message outbox. The interface of our message outbox looks as follows:

```python
# blog/examples/src/outbox_pattern/outbox/message_outbox.py

class IMessageOutbox(ABC):
    @abstractmethod
    def save(self, event: Event) -> None:
        pass

    @abstractmethod
    def mark_as_published(self, message: OutboxMessage) -> None:
        pass

    @abstractmethod
    def to_publish(self) -> list[OutboxMessage]:
        pass

```

I decided to go with an SQLAlchemy implementation:

```python
# blog/examples/src/outbox_pattern/outbox/sql_alchemy_message_outbox.py

class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    id = Column(CHAR(32), primary_key=True)
    occurred_on = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    processed_on = Column(DateTime)

    def __str__(self) -> str:
        return (
            f"OutboxMessage(id={self.id}, occurred_on={self.occurred_on}, "
            f"type={self.type}, processed_on={self.processed_on})"
        )


class SqlAlchemyMessageOutbox(IMessageOutbox):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_outbox_message(self, model: OutboxMessageModel) -> OutboxMessage:
        return OutboxMessage(
            id=EntityId.of(model.id),
            occurred_on=model.occurred_on,
            type=MessageType(model.type),
            data=model.data,
            processed_on=model.processed_on,
        )

    def save(self, event: Event) -> None:
        data = asdict(event)
        outbox_message = OutboxMessageModel(
            id=str(EntityId.new_one()),
            occurred_on=datetime.utcnow(),
            type=f"{type(event).__module__}.{type(event).__name__}",
            data=data,
        )
        self._session.add(outbox_message)

    def to_publish(self) -> list[OutboxMessage]:
        stmt = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.processed_on == null())
            .order_by(OutboxMessageModel.occurred_on)
            .limit(100)
        )

        models: list[OutboxMessageModel] = self._session.execute(stmt).scalars().all()

        result = []
        for model in models:
            result.append(self._to_outbox_message(model))

        return result

    def mark_as_published(self, message: OutboxMessage) -> None:
        self._session.merge(
            OutboxMessageModel(
                id=str(message.id),
                occurred_on=message.occurred_on,
                type=str(message.type),
                data=message.data,
                processed_on=datetime.utcnow(),
            )
        )

```

As you can see above:
- the `save` method takes the `event` as an argument, converts it to `OutboxMessageModel`,
and saves it in the database. The `type` property is the fully qualified class name.
The `data` property is a serialized event’s data.
- the `to_publish` method returns all messages that have processed_on property equal to null
- the `mark_as_published` takes the message and set up the `processed_on` property to the `datetime.utcnow()` value.

Then we want to pass our message outbox as a dependency to our `EventBus`.

```python
# blog/examples/src/outbox_pattern/shared/event_bus.py

class IEventBus(ABC):
    @abstractmethod
    def publish(self, event: Event) -> None:
        pass


class StoreAndForwardEventBus(IEventBus):
    def __init__(self, message_outbox: IMessageOutbox) -> None:
        self._message_outbox = message_outbox

    def publish(self, event: Event) -> None:
        self._message_outbox.save(event)

```


The last component is the outbox processor.
The one that is responsible for fetching unprocessed messages from the database, processing them, and saving again with the `processed_on` property set up to the correct value.

```python
# blog/examples/src/outbox_pattern/outbox/outbox_processor.py

class OutboxProcessor:
    def __init__(
        self,
        message_outbox: IMessageOutbox,
        session: Session,
        messenger: Apos
    ) -> None:
        self._message_outbox = message_outbox
        self._session = session
        self._messenger = messenger
        self._logger: FilteringBoundLogger = structlog.get_logger()

    def _get_cls_for(self, message_type: MessageType) -> Type:
        module = importlib.import_module(message_type.module_name())
        return getattr(module, message_type.class_name())  # type: ignore

    def process_outbox_message(self) -> None:
        with self._session.begin():
            messages = self._message_outbox.to_publish()

            for message in messages:
                event_cls = self._get_cls_for(message.type)
                event = event_cls(**message.data)
                self._messenger.publish_event(event)
                self._logger.info(f"Publishing event {event}")
                self._message_outbox.mark_as_published(message)

```



The procedure is as follows:
1. Get all messages that need to be published
2. Build the concrete event instance based on the fully qualified class name saved in the database
3. Publish the event using some messaging library. For this article, I used apos
4. Save this message as published, so it won’t be processed during the next execution.

If anything went wrong during point 3 the message won’t be marked as processed.
`OutboxProcessor` will try to process it again during the next execution.

As I mentioned before `OutboxProcessor` needs to run periodically
(I used [rocketry](https://github.com/Miksus/rocketry) to accomplish it.
If you haven’t heard about this library I encourage you to check it out.
It’s powerful, lightweight, and very easy to use).

```python
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

```

## Summary

I hope you enjoyed it.
Don't hesitate to check out the full code on my [GitHub](https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/src/outbox_pattern).
I would love to hear your opinion.

I presented you with the outbox pattern in Python.
I hope that by using this technique your system will have reliable messaging and guaranteed delivery of events.

Let me know in case of any questions :wink:.
