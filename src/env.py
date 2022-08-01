import dataclasses
from pathlib import Path
from typing import Dict

from src.ast import Node
from src.errs import Errors, CompilationError


@dataclasses.dataclass
class Project:
    root: Path
    root_packages: Dict[str, Path]


@dataclasses.dataclass
class Compiler:
    project: Project
    errors: Errors

    def add_error_to_node(self, node: Node, message: str, hint: str):
        self.errors.add_error(CompilationError(span=node.span, message=message, hint=hint, filepath=node.module().path))

    def add_error(self, err: CompilationError):
        self.errors.add_error(err)
