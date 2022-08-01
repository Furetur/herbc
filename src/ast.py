import dataclasses
from pathlib import Path
from typing import Union, List, Tuple

from src.span import Span


@dataclasses.dataclass(kw_only=True)
class Node:
    span: Span
    parent: Union['Node', None]

    def module(self) -> 'Module':
        if type(self) is Module:
            self: 'Module'
            return self
        else:
            assert self.parent is not None
            return self.parent.module()


@dataclasses.dataclass(kw_only=True)
class Decl(Node):
    pass


@dataclasses.dataclass(kw_only=True)
class Import(Decl):
    alias: str
    path: Tuple[str]
    is_relative: bool

    imported_module: 'Module' = None

    def has_alias(self) -> bool:
        return self.alias != ""

    def import_path(self) -> str:
        if self.is_relative:
            return "." + ".".join(self.path)
        else:
            return ".".join(self.path)

    def resolved_path(self) -> Path:
        assert self.imported_module is not None
        return self.imported_module.path


@dataclasses.dataclass(kw_only=True)
class Module(Node):
    path: Path
    imports: List[Import]
