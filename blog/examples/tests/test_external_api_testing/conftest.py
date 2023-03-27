import logging
from logging import Logger

import pytest


@pytest.fixture
def test_logger() -> Logger:
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)

    return logger
