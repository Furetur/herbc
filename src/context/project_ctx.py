import dataclasses
from pathlib import Path
from typing import Dict

from src.defs.constants import BUILD_DIR_NAME


@dataclasses.dataclass
class ProjectCtx:
    root: Path
    runtime: Path
    root_packages: Dict[str, Path]

    def build_dir(self):
        return self.root / BUILD_DIR_NAME
