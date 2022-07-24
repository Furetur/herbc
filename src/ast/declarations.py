import dataclasses
from typing import List

from src.ast.node import Node


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


@dataclasses.dataclass()
class ImportPath(Node):
    path: List[str]
    is_relative: bool
