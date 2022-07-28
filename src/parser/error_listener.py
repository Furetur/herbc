from pathlib import Path

import antlr4
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import ParseCancellationException

from src.defs.env import Compiler
from src.defs.errs import CompilationError
from src.defs.pos import Pos


class HerbErrorListener(ErrorListener):
    def __init__(self, compiler: Compiler, filepath: Path):
        self.compiler = compiler
        self.path = filepath
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.compiler.add_error(CompilationError(
            pos=Pos(filepath=self.path, line=line, column=column),
            message=msg,
            hint="this is a parsing error."
        ))
        self.has_errors = True
