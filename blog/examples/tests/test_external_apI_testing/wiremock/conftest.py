import pytest
import requests
from requests import RequestException
from wiremock.constants import Config


@pytest.fixture()
def wiremock_base_url() -> str:
    return "http://localhost:8080"


@pytest.fixture
def wiremock(wiremock_base_url: str) -> None:
    wiremock_admin_url = f"{wiremock_base_url}/__admin"
    Config.base_url = wiremock_admin_url

    try:
        response = requests.get(wiremock_admin_url)
        response.raise_for_status()
    except RequestException:
        pytest.fail("You forget to run wiremock! Please run the container from `docker-compose.yml` file")
