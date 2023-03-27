from logging import Logger

import pytest
import responses

from src.external_api_testing.email_address import EmailAddress
from src.external_api_testing.university_email_address_validator import HipoLabsUniversityEmailAddressValidator


@pytest.fixture
def hipo_base_url() -> str:
    return "http://universities.hipolabs.dev.com"


@pytest.fixture
def hipo_email_address_validator(hipo_base_url: str, test_logger: Logger) -> HipoLabsUniversityEmailAddressValidator:
    return HipoLabsUniversityEmailAddressValidator(hipo_base_url, test_logger)


@responses.activate
def test_should_correctly_validate_university_email_address(
    hipo_base_url: str, hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator
) -> None:
    # given
    responses.add(
        responses.GET,
        f"{hipo_base_url}/search?domain=zut.edu.pl",
        json=[
            {
                "state-province": None,
                "domains": ["zut.edu.pl"],
                "country": "Poland",
                "web_pages": ["http://www.zut.edu.pl/"],
                "name": "Zachodniopomorska School of Science and Engineering",
                "alpha_two_code": "PL",
            }
        ],
        status=200,
    )

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is True


@responses.activate
def test_should_correctly_validate_non_university_email_address(
    hipo_base_url: str,
    hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator,
) -> None:
    # given
    responses.add(
        responses.GET,
        f"{hipo_base_url}/search?domain=gmail.com",
        json=[],
        status=200,
    )

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@gmail.com"))

    # then
    assert result is False


@responses.activate
def test_should_fail_validation_if_network_error(
    hipo_base_url: str, hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator
) -> None:
    # given
    responses.add(
        responses.GET,
        f"{hipo_base_url}/search?domain=zut.edu.pl",
        status=503,
    )
    responses.add(
        responses.GET,
        f"{hipo_base_url}/search?domain=edu.pl",
        status=503,
    )

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is False
