from pathlib import Path

import pytest
from paramiko import SSHClient

from szymonmiks_deployment.config import FTPConfig
from szymonmiks_deployment.ftp_client import ParamikoFTPClient


@pytest.fixture
def upload_file() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "upload.json"


@pytest.mark.usefixtures("clean_up_sftp")
def test_can_get_file_from_the_sftp_server(ftp_config: FTPConfig, ssh_client: SSHClient, upload_file: Path) -> None:
    # given
    ssh_client.connect(
        hostname=ftp_config.host,
        username=ftp_config.username,
        password=ftp_config.password,
        port=ftp_config.port,
    )
    sftp = ssh_client.open_sftp()
    sftp.put(str(upload_file), f"{ftp_config.path}/{upload_file.name}")
    client = ParamikoFTPClient(ssh_client, ftp_config)

    # when
    local_path = Path("test_from_sftp.json")
    client.get(Path("upload.json"), local_path)

    # then
    assert local_path.is_file()
    local_path.unlink(missing_ok=True)


@pytest.mark.usefixtures("clean_up_sftp")
def test_can_put_file_to_the_sftp_server(ftp_config: FTPConfig, ssh_client: SSHClient, upload_file: Path) -> None:
    # given
    client = ParamikoFTPClient(ssh_client, ftp_config)

    # when
    client.put(upload_file.absolute(), Path("upload.json"))

    # then
    sftp = ssh_client.open_sftp()
    assert upload_file.name in sftp.listdir(ftp_config.path)
    sftp.close()
