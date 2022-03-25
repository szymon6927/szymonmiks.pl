from dataclasses import dataclass


@dataclass(frozen=True)
class SSH2PublicKey:
    key: str

    def __post_init__(self) -> None:
        if not self.key.startswith(
            "---- BEGIN SSH2 PUBLIC KEY ----"
        ) and not self.key.endswith("---- END SSH2 PUBLIC KEY ----"):
            raise ValueError("Provided SSH2 public key has incorrect format!")

    def __str__(self) -> str:
        return self.key
