from src.outbox_pattern.outbox.message import MessageType


def test_can_get_module_name_and_class_name() -> None:
    # given
    message_type = MessageType("src.outbox_pattern.library.domain.event.TestEvent")

    # then
    assert message_type.module_name() == "src.outbox_pattern.library.domain.event"
    assert message_type.class_name() == "TestEvent"
