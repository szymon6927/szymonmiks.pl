from dataclasses import dataclass


@dataclass(frozen=True)
class OpenSSHPublicKey:
    key: str

    def __post_init__(self) -> None:
        if "ssh-rsa" not in self.key:
            raise ValueError("Provided OpenSSH key has incorrect format!")

    def __str__(self) -> str:
        return self.key
