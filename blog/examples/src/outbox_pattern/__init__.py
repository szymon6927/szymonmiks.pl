from apos import Apos

from src.outbox_pattern.library.domain.events import LibraryCardCreated
from src.outbox_pattern.notifications.handlers import library_card_created_event_handler

messenger = Apos()
messenger.subscribe_event(LibraryCardCreated, [library_card_created_event_handler])
