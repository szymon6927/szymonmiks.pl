import logging
from logging import Logger

import pytest
import responses
from requests import HTTPError

from src.external_api_retry.email_address import EmailAddress
from src.external_api_retry.university_email_address_validator import HipoLabsUniversityEmailAddressValidator


@pytest.fixture
def test_logger() -> Logger:
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)

    return logger


@pytest.fixture
def hipo_base_url() -> str:
    return "http://universities.hipolabs.dev.com"


@pytest.fixture
def hipo_email_address_validator(hipo_base_url: str, test_logger: Logger) -> HipoLabsUniversityEmailAddressValidator:
    return HipoLabsUniversityEmailAddressValidator(hipo_base_url, test_logger)


@responses.activate
def test_should_retry_if_any_http_error_occurred(
    hipo_base_url: str, hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator
) -> None:
    # given
    responses.add(responses.GET, f"{hipo_base_url}/search?domain=zut.edu.pl", body=HTTPError())

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is False
    responses.assert_call_count(f"{hipo_base_url}/search?domain=zut.edu.pl", 3)
