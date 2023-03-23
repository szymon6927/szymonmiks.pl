from logging import Logger
from unittest.mock import Mock, patch

import pytest

from src.external_api_testing.email_address import EmailAddress
from src.external_api_testing.university_email_address_validator import HipoLabsUniversityEmailAddressValidator


@pytest.fixture
def hipo_base_url() -> str:
    return "http://universities.hipolabs.dev.com"


@pytest.fixture
def hipo_email_address_validator(hipo_base_url: str, test_logger: Logger) -> HipoLabsUniversityEmailAddressValidator:
    return HipoLabsUniversityEmailAddressValidator(hipo_base_url, test_logger)


@patch("src.external_api_testing.university_email_address_validator.requests")
def test_should_correctly_validate_university_email_address(
    mock_requests: Mock, hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator
) -> None:
    # given
    mock_requests.get.return_value.status_code.return_value = 200
    mock_requests.get.return_value.json.return_value = [
        {
            "state-province": None,
            "domains": ["zut.edu.pl"],
            "country": "Poland",
            "web_pages": ["http://www.zut.edu.pl/"],
            "name": "Zachodniopomorska School of Science and Engineering",
            "alpha_two_code": "PL",
        }
    ]

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is True


@patch("src.external_api_testing.university_email_address_validator.requests")
def test_should_correctly_validate_non_university_email_address(
    mock_requests: Mock, hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator
) -> None:
    # given
    mock_requests.get.return_value.status_code.return_value = 200
    mock_requests.get.return_value.json.return_value = []

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@gmail.com"))

    # then
    assert result is False
