import dataclasses
from pathlib import Path

from src.ast import Node
from src.ast.utils import module
from src.context.project_ctx import ProjectCtx
from src.context.error_ctx import ErrorCtx, CompilationError


@dataclasses.dataclass
class CompilationCtx:
    project: ProjectCtx
    errors: ErrorCtx
    outpath: Path

    def add_error_to_node(self, node: Node, message: str, hint=""):
        self.errors.add_error(CompilationError(span=node.span, message=message, hint=hint, filepath=module(node).path))

    def add_error(self, err: CompilationError):
        self.errors.add_error(err)

    def has_errors(self) -> bool:
        return self.errors.has_errors()
