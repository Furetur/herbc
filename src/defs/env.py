import dataclasses
from pathlib import Path
from typing import Dict

from src.ast.node import Node
from src.defs.errs import Errors, CompilationError
from src.defs.pos import Pos


@dataclasses.dataclass()
class Project:
    root: Path
    root_packages: Dict[str, Path]


@dataclasses.dataclass()
class Compiler:
    project: Project
    errors: Errors

    def add_error_to_node(self, node: Node, message: str, hint: str):
        self.errors.add_error(CompilationError(pos=node.pos, message=message, hint=hint))

    def add_error(self, err: CompilationError):
        self.errors.add_error(err)
