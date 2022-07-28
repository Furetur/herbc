import dataclasses
from typing import List

from src.defs.pos import Pos


class CompilationInterrupted(Exception):
    """
    This exception stops the compilation process.
    """
    def __init__(self, message="There are compilation errors!"):
        self.message = message


@dataclasses.dataclass
class CompilationError:
    pos: Pos
    message: str
    hint: str

    def __str__(self):
        return f"{self.pos}: {self.message}\n\tHint: {self.hint}"


class Errors:
    errors: List[CompilationError]

    def __init__(self):
        self.errors = []

    def add_error(self, err: CompilationError):
        self.errors.append(err)

    def print_errors(self):
        for err in self.errors:
            print(err)
