import structlog

from src.outbox_pattern.library.domain.events import LibraryCardCreated

LOGGER = structlog.get_logger()


def library_card_created_event_handler(event: LibraryCardCreated) -> None:
    LOGGER.info("library_card_created_event_handler invoked!")
    LOGGER.info(f"Event = {event}")
