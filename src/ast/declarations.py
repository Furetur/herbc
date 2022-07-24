import dataclasses
from pathlib import Path
from typing import List, Tuple

from src.ast.node import Node
from src.defs.env import ProjectEnvironment


class Decl(Node):
    pass


@dataclasses.dataclass()
class Import(Decl):
    alias: str
    import_path: 'ImportPath'

    @staticmethod
    def with_alias(alias: str, import_path: 'ImportPath') -> 'Import':
        return Import(alias=alias, import_path=import_path)

    @staticmethod
    def without_alias(import_path: 'ImportPath') -> 'Import':
        return Import(alias="", import_path=import_path)

    def has_alias(self) -> bool:
        return self.alias != ""


@dataclasses.dataclass(frozen=True)
class ImportPath(Node):
    path: Tuple[str]
    is_relative: bool

    def abs_path(self, proj: ProjectEnvironment):
        assert len(self.path) > 0 or self.is_relative
        if len(self.path) == 0:
            return proj.root
        root = proj.root if self.is_relative else proj.root_packages[self.path[0]]
        path_tail = Path("")
        for p in (self.path if self.is_relative else self.path[1:]):
            path_tail = path_tail / p
        return root / path_tail
