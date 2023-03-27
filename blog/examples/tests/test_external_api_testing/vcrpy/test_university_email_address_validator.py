from logging import Logger
from pathlib import Path

import pytest
import vcr

from src.external_api_testing.email_address import EmailAddress
from src.external_api_testing.university_email_address_validator import HipoLabsUniversityEmailAddressValidator


@pytest.fixture
def hipo_base_url() -> str:
    return "http://universities.hipolabs.com"


@pytest.fixture
def hipo_email_address_validator(hipo_base_url: str, test_logger: Logger) -> HipoLabsUniversityEmailAddressValidator:
    return HipoLabsUniversityEmailAddressValidator(hipo_base_url, test_logger)


@vcr.use_cassette(str(Path(__file__).parent / "correct_university_email_address.yaml"))
def test_should_correctly_validate_university_email_address(
    hipo_base_url: str, hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator
) -> None:
    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is True


@vcr.use_cassette(str(Path(__file__).parent / "incorrect_university_email_address.yaml"))
def test_should_correctly_validate_non_university_email_address(
    hipo_base_url: str,
    hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator,
) -> None:
    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@gmail.com"))

    # then
    assert result is False
