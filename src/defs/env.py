import dataclasses
from pathlib import Path
from typing import Dict


@dataclasses.dataclass()
class ProjectEnvironment:
    root: Path
    root_packages: Dict[str, Path]
