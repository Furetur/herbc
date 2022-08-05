import dataclasses
from pathlib import Path
from typing import List

from src.span import Span


class CompilationInterrupted(Exception):
    """
    This exception stops the compilation process.
    """
    def __init__(self, message="There are compilation errors!"):
        self.message = message


@dataclasses.dataclass
class CompilationError:
    filepath: Path
    span: Span
    message: str
    hint: str

    def __str__(self):
        if self.hint != "":
            return f"{self.filepath}:{self.span}: {self.message}\n\tHint: {self.hint}"
        else:
            return f"{self.filepath}:{self.span}: {self.message}\n"


class ErrorCtx:
    errors: List[CompilationError]

    def __init__(self):
        self.errors = []

    def add_error(self, err: CompilationError):
        self.errors.append(err)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_errors(self):
        for err in self.errors:
            print(err)
