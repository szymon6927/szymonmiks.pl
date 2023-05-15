from abc import ABC, abstractmethod
from logging import Logger

import requests
from requests import RequestException
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.external_api_retry.email_address import EmailAddress


class HipoLabsValidationError(Exception):
    pass


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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        retry=retry_if_exception_type(HipoLabsValidationError),
    )
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
            raise HipoLabsValidationError from error

    def validate(self, email: EmailAddress) -> bool:
        domain = email.domain

        try:
            if self._is_university_domain(domain):
                return True

            # skip suffix if email contains department name eg. @eti.pg.gda.pl -> the real domain is pg.gda.pl
            for part in domain.split(".")[:-2]:
                domain = domain[len(f"{part}.") :]  # noqa: E203

                if self._is_university_domain(domain):
                    return True

            return False
        except RetryError as error:
            self._logger.exception(
                f"An RetryError occurred. Error = {error}. "
                f"Retry statistics {self._is_university_domain.retry.statistics}"  # type: ignore
            )
            return False
