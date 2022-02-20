from abc import ABC, abstractmethod
from pathlib import Path

from paramiko import SSHClient

from szymonmiks_deployment.config import FTPConfig
from szymonmiks_deployment.logger import LoggerFactory


class IFTPClient(ABC):
    @abstractmethod
    def get(self, remote_path: Path, local_path: Path) -> None:
        pass

    @abstractmethod
    def put(self, local_path: Path, remote_path: Path) -> None:
        pass


class ParamikoFTPClient(IFTPClient):
    def __init__(self, client: SSHClient, config: FTPConfig) -> None:
        self._client = client
        self._config = config
        self._logger = LoggerFactory.create(__name__)

        self._client.connect(
            hostname=self._config.host,
            username=self._config.username,
            password=self._config.password,
            port=self._config.port,
        )
        self._sftp = self._client.open_sftp()
        self._sftp.chdir(self._config.path)

    def get(self, remote_path: Path, local_path: Path) -> None:
        self._logger.info(f"Downloading {remote_path} to {local_path}")
        self._sftp.get(str(remote_path), str(local_path))

    def put(self, local_path: Path, remote_path: Path) -> None:
        self._logger.info(f"Uploading {local_path} to {self._config.path}/{remote_path}")

        if local_path.is_dir():
            self._logger.info("Is dir!")
            try:
                self._sftp.mkdir(str(remote_path))
            except IOError:
                self._logger.info(f"Directory {remote_path} already exists!")
            return

        self._sftp.put(str(local_path), str(remote_path))

    def __del__(self) -> None:
        if self._client:
            self._client.close()
