from typing import Generator

import pytest
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
from paramiko.sftp_client import SFTPClient

from szymonmiks_deployment.config import FTPConfig


@pytest.fixture
def ftp_config() -> FTPConfig:
    return FTPConfig(host="localhost", username="foo", password="pass", path="/upload", port=2222)


@pytest.fixture
def ssh_client() -> SSHClient:
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())

    return ssh_client


def _sftp_rm(path: str, sftp: SFTPClient) -> None:
    files = sftp.listdir(path)

    for f in files:
        filepath = f"{path}/{f}"
        try:
            sftp.remove(filepath)
        except IOError:
            _sftp_rm(filepath, sftp)

    try:
        sftp.rmdir(path)
    except Exception:
        pass


@pytest.fixture
def clean_up_sftp(ssh_client: SSHClient, ftp_config: FTPConfig) -> Generator[None, None, None]:
    yield
    ssh_client.connect(
        hostname=ftp_config.host,
        username=ftp_config.username,
        password=ftp_config.password,
        port=ftp_config.port,
    )
    sftp = ssh_client.open_sftp()
    sftp.chdir(ftp_config.path)
    sftp = ssh_client.open_sftp()

    _sftp_rm(ftp_config.path, sftp)
    sftp.close()
