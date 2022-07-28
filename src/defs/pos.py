import dataclasses
from pathlib import Path


@dataclasses.dataclass()
class Pos:
    filepath: Path
    line: int
    column: int

    def __str__(self):
        return f"{self.filepath}:{self.line}:{self.column}"
