from pathlib import Path

import pytest
from paramiko import SSHClient

from szymonmiks_deployment.config import FTPConfig
from szymonmiks_deployment.deployment_manager import DeploymentManager
from szymonmiks_deployment.file_collector import WebsiteFileCollector
from szymonmiks_deployment.ftp_client import ParamikoFTPClient


@pytest.mark.usefixtures("clean_up_sftp")
def test_deploy(ftp_config: FTPConfig, ssh_client: SSHClient) -> None:
    # given
    sftp_client = ParamikoFTPClient(ssh_client, ftp_config)
    base_dir = Path(__file__).parent.parent.parent.parent
    file_collector = WebsiteFileCollector(base_dir)
    deployment_manager = DeploymentManager(sftp_client, file_collector)

    # when
    deployment_manager.deploy()

    # then
    sftp = ssh_client.open_sftp()
    sftp_dir_list = sftp.listdir(ftp_config.path)
    assert "index.html" in sftp_dir_list
    assert "css" in sftp_dir_list
    assert "cv" in sftp_dir_list
    assert "img" in sftp_dir_list
    assert "js" in sftp_dir_list
    assert "szymonmiks-deployment" not in sftp_dir_list
    assert "video" in sftp_dir_list
    assert "404.html" in sftp_dir_list
    assert "szymon_miks_cv.pdf" in sftp_dir_list
    sftp.close()
