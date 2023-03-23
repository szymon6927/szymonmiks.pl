from abc import ABC, abstractmethod
from logging import Logger

import requests
from requests import RequestException

from src.external_api_testing.email_address import EmailAddress


class IUniversityEmailAddressValidator(ABC):
    @abstractmethod
    def validate(self, email: EmailAddress) -> bool:
        ...


class HipoLabsUniversityEmailAddressValidator(IUniversityEmailAddressValidator):
    """
    External API service for searching the university based on domain
    https://github.com/Hipo/university-domains-list/
    http://universities.hipolabs.com/search
    """

    def __init__(self, base_url: str, logger: Logger) -> None:
        self._base_url = base_url
        self._logger = logger

    def _is_university_domain(self, domain: str) -> bool:
        try:
            self._logger.info("Checking `%s` with HipooLabsClient", domain)

            url = f"{self._base_url}/search?domain={domain}"
            response = requests.get(url=url, timeout=(2, 3))
            response.raise_for_status()

            self._logger.info("Response [%s] json = %s", response.status_code, response.json())

            # If number of records in the response is greater than 0 it means that domain belongs to university
            return len(response.json()) > 0
        except RequestException as error:
            self._logger.error("An error occurred during domain verification!")
            self._logger.error("Error = %s", str(error))
            return False

    def validate(self, email: EmailAddress) -> bool:
        domain = email.domain

        if self._is_university_domain(domain):
            return True

        # skip suffix if email contains department name eg. @eti.pg.gda.pl -> the real domain is pg.gda.pl
        for part in domain.split(".")[:-2]:
            domain = domain[len(f"{part}."):]

            if self._is_university_domain(domain):
                return True

        return False
