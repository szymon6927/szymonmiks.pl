from logging import Logger

import pytest
from wiremock.resources.mappings import HttpMethods, Mapping, MappingRequest, MappingResponse
from wiremock.resources.mappings.resource import Mappings

from src.external_api_testing.email_address import EmailAddress
from src.external_api_testing.university_email_address_validator import HipoLabsUniversityEmailAddressValidator


@pytest.fixture
def hipo_email_address_validator(
    wiremock_base_url: str, test_logger: Logger
) -> HipoLabsUniversityEmailAddressValidator:
    return HipoLabsUniversityEmailAddressValidator(wiremock_base_url, test_logger)


@pytest.mark.usefixtures("wiremock")
def test_should_correctly_validate_university_email_address(
    hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator,
) -> None:
    # given
    mapping = Mapping(
        request=MappingRequest(method=HttpMethods.GET, url="/search?domain=zut.edu.pl"),
        response=MappingResponse(
            status=200,
            json_body=[
                {
                    "state-province": None,
                    "domains": ["zut.edu.pl"],
                    "country": "Poland",
                    "web_pages": ["http://www.zut.edu.pl/"],
                    "name": "Zachodniopomorska School of Science and Engineering",
                    "alpha_two_code": "PL",
                }
            ],
        ),
    )
    Mappings.create_mapping(mapping=mapping)

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is True


@pytest.mark.usefixtures("wiremock")
def test_should_correctly_validate_non_university_email_address(
    hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator,
) -> None:
    # given
    mapping = Mapping(
        request=MappingRequest(method=HttpMethods.GET, url="/search?domain=gmail.com"),
        response=MappingResponse(status=200, json_body=[]),
    )
    Mappings.create_mapping(mapping=mapping)

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@gmail.com"))

    # then
    assert result is False


@pytest.mark.usefixtures("wiremock")
def test_should_fail_validation_if_network_error(
    hipo_email_address_validator: HipoLabsUniversityEmailAddressValidator,
) -> None:
    # given
    Mappings.create_mapping(
        Mapping(
            request=MappingRequest(method=HttpMethods.GET, url="/search?domain=zut.edu.pl"),
            response=MappingResponse(fault="CONNECTION_RESET_BY_PEER"),
        )
    )
    Mappings.create_mapping(
        Mapping(
            request=MappingRequest(method=HttpMethods.GET, url="/search?domain=edu.pl"),
            response=MappingResponse(fault="CONNECTION_RESET_BY_PEER"),
        )
    )

    # when
    result = hipo_email_address_validator.validate(EmailAddress("john.deo@zut.edu.pl"))

    # then
    assert result is False
