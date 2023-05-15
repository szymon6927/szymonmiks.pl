+++
author = "Szymon Miks"
title = "How to retry an API request to the external system"
description = "In this blog post, I will show you how to implement a retry mechanism for external API requests in Python"
date = "2023-06-01"
image = "img/headway-5QgIuuBxKwM-unsplash.jpg"
categories = [
     "Python", "Software_Development"
]
tags = [
    "python",
    "software development",
    "testing",
    "pytest",
    "responses",
    "vcrpy",
    "wiremock",
    "external api"
]
draft = false
+++

## Intro

Today I want to show you how to implement a **retry mechanism** the external API requests in Python.

Before we jump straight to the code let me explain what the **retry mechanism** is.

In software engineering, a **retry mechanism** is a way to automatically repeat an action that has failed,
in the hopes that the action will succeed on a subsequent attempt.
This is often used when dealing with unreliable or flaky systems, where it's possible that a request or operation might fail due to transient issues such as network timeouts, server errors, or other temporary glitches.

Instead of immediately giving up and reporting an error to the user, the software will retry the failed action a certain number of times, with a short delay between each attempt.
If the action eventually succeeds, the software will continue as normal; if the action continues to fail after all the retries, it will report an error to the user.

That's all when it comes to the **retry mechanism** description itself.

To complete the description section I have to mention a few other terms:
- **Retry Limit** - This is the maximum number of times that the action will be retried before giving up and reporting an error.
The retry limit is often configurable and can be set based on the specific needs of the software and the system it's interacting with.

- **Backoff** - This refers to the delay between each retry attempt.
The idea behind backoff is to introduce a progressively longer delay between retries, to avoid overwhelming the system with repeated requests.
For example, the backoff might start with a short delay of a few seconds, and then double with each subsequent retry.

- **Backoff Strategy** - This refers to the specific algorithm used to determine the delay between each retry attempt.
There are several backoff strategies, including fixed, linear, exponential, and jittered backoff.
Each strategy has its own strengths and weaknesses and is suitable for different use cases.

- **Backoff Rate** - This is the factor by which the delay between retries is multiplied in each iteration of the backoff.
For example, if the initial delay is 1 second and the backoff rate is 2, the delay between the first and second retries will be 2 seconds, the delay between the second and third retries will be 4 seconds, and so on.


For this blogpost purpose, we will use a **retry mechanism** for the API HTTP requests to the external system.
In the [previous blogpost](/p/how-to-test-an-api-request-to-the-external-system/) I described how to test API requests to the external system.
We will use that code to implement the retry mechanism.

## Code

I'm using the [tenacity](https://github.com/jd/tenacity) library to implement the **retry mechanism**.
I recommend this library. I have used it in production, it works very well.
It has a lot of options, and it is very easy to configure.
Basically, all we need to do is to add the `@retry` decorator to the functions.

```python
# blog/examples/src/external_api_retry/university_email_address_validator.py

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
                domain = domain[len(f"{part}.") :]

                if self._is_university_domain(domain):
                    return True

            return False
        except RetryError as error:
            self._logger.exception(
                f"An RetryError occurred. Error = {error}. Retry statistics {self._is_university_domain.retry.statistics}"  # type: ignore
            )
            return False

```

and the tests to check if our **retry** works as expected:

```python
# blog/examples/tests/test_retry_mechanism/test_university_email_address_validator.py

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

```

At this stage, I wanted to mention one more thing.
Using [tenacity](https://github.com/jd/tenacity) is not the only option.
There is a possibility to implement a **retry mechanism** using the [urllib3 retry object](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html).
I didn't show you this in the code example because of one simple reason: it is very hard to write a unit test for this solution.

In one of my previous projects, I tried to write unit tests for retry implemented using the [urllib3 retry object](https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html).
I failed :pensive_face:.

First of all, it is not possible to use libraries like [responses](https://github.com/getsentry/responses) or [request-mock](https://requests-mock.readthedocs.io/en/latest/) - they don't have support for it.
The only option is some dirty hacks with `@patch` - you can read more about it [here](https://stackoverflow.com/a/72302191).

If you know how to achieve it, using **clean** methods without using `@patch`, please let me know.
I would love to see the solution :slightly_smiling_face:.

## Summary

Overall, the "retry" mechanism is a useful tool in software engineering for dealing with unreliable systems and ensuring that actions that can't be completed on the first try are still able to eventually succeed.

It is very popular and common practice especially when it comes to **microservices architecture**.
I hope you know the first fallacy from the [Fallacies of distributed computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing).
This is **"The network is reliable"**.
Having that in mind we as developer needs to put as much effort as we can to minimize the risk and try to guarantee robust communication between our systems.

That's all, I hope you enjoyed it :slightly_smiling_face:.
Let me know what your opinion about the **retry mechanism** is. Did you implement it?
Have you encountered some problems during implementation?
I would like to see your perspective :slightly_smiling_face:
