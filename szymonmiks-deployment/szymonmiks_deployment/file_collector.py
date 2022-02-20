from pathlib import Path
from typing import List


class FileCollector:
    EXCLUDED = ["szymonmiks-deployment", ".git", ".idea", ".gitignore", "README.md"]

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir

    @property
    def base_dir(self) -> Path:
        return self._base_dir

    def collect(self) -> List[Path]:
        file_list = []

        for p in self._base_dir.rglob("*"):
            if any(excluded in p.parts for excluded in self.EXCLUDED):
                continue

            if p.name.startswith("."):
                continue

            file_list.append(p)

        return file_list
