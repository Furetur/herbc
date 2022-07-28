import dataclasses
from pathlib import Path
from typing import List, Tuple

from src.ast.node import Node
from src.defs.env import Project
from src.defs.pos import Pos


class Decl(Node):
    pass


@dataclasses.dataclass()
class Import(Decl):
    alias: str
    path: Tuple[str]
    is_relative: bool
    pos: Pos

    resolved_path: Path = None

    def has_alias(self) -> bool:
        return self.alias != ""

    def import_path(self) -> str:
        if self.is_relative:
            return "." + ".".join(self.path)
        else:
            return ".".join(self.path)
