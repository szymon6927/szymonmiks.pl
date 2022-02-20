from szymonmiks_deployment.file_collector import FileCollector
from szymonmiks_deployment.ftp_client import IFTPClient
from szymonmiks_deployment.logger import LoggerFactory


class DeploymentManager:
    def __init__(self, client: IFTPClient, file_collector: FileCollector) -> None:
        self._client = client
        self._file_collector = file_collector
        self._logger = LoggerFactory.create(__name__)

    def deploy(self) -> None:
        self._logger.info("Start deployment!")

        files_to_upload = self._file_collector.collect()

        for file in files_to_upload:
            remote_path = file.relative_to(self._file_collector.base_dir)
            self._client.put(file, remote_path)

        self._logger.info("Deployment has finished!")
