from pathlib import Path

from antlr4 import FileStream, CommonTokenStream

from src.ast import Module
from src.ast.fixverify import set_parents
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.parser.error_listener import HerbErrorListener
from src.parser.generated.HerbLexer import HerbLexer
from src.parser.generated.HerbParser import HerbParser
from src.parser.parser import HerbParserVisitor


def parse(compiler: CompilationCtx, path: Path) -> Module:
    input_stream = FileStream(str(path), encoding='utf-8')
    error_listener = HerbErrorListener(compiler, path)
    lexer = HerbLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    stream = CommonTokenStream(lexer)
    if error_listener.has_errors:
        raise CompilationInterrupted()
    parser = HerbParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.prog()
    if error_listener.has_errors:
        raise CompilationInterrupted()
    mod = tree.accept(HerbParserVisitor(path, compiler))
    set_parents(mod)
    return mod
