import pytest

from src.optimistic_locking.wallet import Version


def test_can_not_create_version_smaller_than_0() -> None:
    # expect
    with pytest.raises(ValueError):
        Version(-1)


def test_can_create_zero_version() -> None:
    # expect
    assert Version.zero() == Version(0)
