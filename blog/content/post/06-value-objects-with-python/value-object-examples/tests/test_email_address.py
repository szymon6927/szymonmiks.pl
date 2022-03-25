import pytest
from value_object_examples.email_address import EmailAddress


def test_can_validate_email_address() -> None:
    # expect
    assert str(EmailAddress("abc.def@mail.cc")) == "abc.def@mail.cc"
    with pytest.raises(ValueError):
        EmailAddress("abc.def@mail.c")


def test_can_check_if_email_is_academical() -> None:
    # expect
    assert str(EmailAddress.academical("john.deo@zut.edu.pl")) == "john.deo@zut.edu.pl"
    assert str(EmailAddress.academical("tom.tailow@pg.edu.pl")) == "tom.tailow@pg.edu.pl"
    with pytest.raises(ValueError):
        EmailAddress.academical("john.deo@gmail.com")


def test_can_change_email_address() -> None:
    # given
    email_address = EmailAddress("john.deo@gmail.com")

    # when
    new_email_address = email_address.change("tom.newman@gmail.com", is_academical=False)

    # then
    assert new_email_address == EmailAddress("tom.newman@gmail.com")


def test_can_change_email_address_to_academical() -> None:
    # given
    email_address = EmailAddress("john.deo@gmail.com")

    # when
    new_email_address = email_address.change("john.deo@zut.edu.pl", is_academical=True)

    # then
    assert new_email_address == EmailAddress("john.deo@zut.edu.pl")
