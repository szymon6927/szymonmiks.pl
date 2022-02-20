from pathlib import Path

from paramiko import AutoAddPolicy, SSHClient

from szymonmiks_deployment.config import FTPConfig
from szymonmiks_deployment.deployment_manager import DeploymentManager
from szymonmiks_deployment.file_collector import FileCollector
from szymonmiks_deployment.ftp_client import ParamikoFTPClient


class DeploymentManagerFactory:
    @staticmethod
    def create() -> DeploymentManager:
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ftp_config = FTPConfig.from_env()

        ftp_client = ParamikoFTPClient(ssh_client, ftp_config)
        base_dir = Path(__file__).parent.parent.parent

        return DeploymentManager(ftp_client, FileCollector(base_dir))
