from pathlib import Path

from antlr4.error.ErrorListener import ErrorListener

from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationError
from src.span import Span


class HerbErrorListener(ErrorListener):
    def __init__(self, compiler: CompilationCtx, filepath: Path):
        self.compiler = compiler
        self.path = filepath
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.compiler.add_error(CompilationError(
            filepath=self.path,
            span=Span(line=line, column=column),
            message=msg,
            hint="this is a parsing error."
        ))
        self.has_errors = True
