from dataclasses import dataclass
from os import environ


class FTPConfigError(Exception):
    pass


@dataclass(frozen=True)
class FTPConfig:
    host: str
    username: str
    password: str
    path: str
    port: int = 22

    def __post_init__(self) -> None:
        if any(elem == "" for elem in [self.host, self.username, self.path, self.password]):
            raise FTPConfigError("None of the properties can be empty!")

    @classmethod
    def from_env_for_website(cls) -> "FTPConfig":
        try:
            host = environ["FTP_HOST"]
            username = environ["FTP_USERNAME"]
            password = environ["FTP_PASSWORD"]
            path = environ["FTP_PATH"]

            return cls(host=host, username=username, password=password, path=path)
        except Exception as error:
            raise FTPConfigError("Can not build FTPConfig fron env vars!") from error

    @classmethod
    def from_env_for_blog(cls) -> "FTPConfig":
        try:
            host = environ["FTP_HOST"]
            username = environ["FTP_USERNAME"]
            password = environ["FTP_PASSWORD"]
            path = environ["BLOG_FTP_PATH"]

            return cls(host=host, username=username, password=password, path=path)
        except Exception as error:
            raise FTPConfigError("Can not build FTPConfig fron env vars!") from error
