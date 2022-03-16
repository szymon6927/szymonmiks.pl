import pytest
from _pytest.monkeypatch import MonkeyPatch

from szymonmiks_deployment.config import FTPConfig, FTPConfigError


def test_can_build_ftp_config_from_env(monkeypatch: MonkeyPatch) -> None:
    # given
    monkeypatch.setenv("FTP_HOST", "test_host")
    monkeypatch.setenv("FTP_USERNAME", "test_user")
    monkeypatch.setenv("FTP_PASSWORD", "test_password")
    monkeypatch.setenv("FTP_PATH", "test/path/foo/bar")

    # when
    config = FTPConfig.from_env_for_website()

    # then
    assert isinstance(config, FTPConfig)
    assert config.host == "test_host"
    assert config.username == "test_user"
    assert config.password == "test_password"
    assert config.path == "test/path/foo/bar"


def test_should_raise_an_exception_if_any_of_the_value_is_empty(monkeypatch: MonkeyPatch) -> None:
    # given
    monkeypatch.setenv("FTP_HOST", "test_host")
    monkeypatch.setenv("FTP_USERNAME", "")
    monkeypatch.setenv("FTP_PASSWORD", "test_password")
    monkeypatch.setenv("FTP_PATH", "test/path/foo/bar")

    # then
    with pytest.raises(FTPConfigError):
        FTPConfig.from_env_for_website()


def test_should_raise_an_exception_if_missing_env(monkeypatch: MonkeyPatch) -> None:
    # given
    monkeypatch.setenv("FTP_HOST", "test_host")
    monkeypatch.setenv("FTP_PASSWORD", "test_password")
    monkeypatch.setenv("FTP_PATH", "test/path/foo/bar")

    # then
    with pytest.raises(FTPConfigError):
        FTPConfig.from_env_for_website()
