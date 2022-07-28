from pathlib import Path
from typing import Tuple

from antlr4 import FileStream, CommonTokenStream, ParserRuleContext

from src.ast.declarations import Import
from src.ast.module import File
from src.defs.env import Compiler
from src.defs.errs import CompilationInterrupted
from src.defs.pos import Pos
from src.parser.error_listener import HerbErrorListener
from src.parser.generated.HerbLexer import HerbLexer
from src.parser.generated.HerbParser import HerbParser
from src.parser.generated.HerbVisitor import HerbVisitor


def parse(compiler: Compiler, path: Path) -> File:
    input_stream = FileStream(str(path))
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
    return tree.accept(HerbParserVisitor(path))


class HerbParserVisitor(HerbVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def visitProg(self, ctx: HerbParser.ProgContext) -> File:
        imports = []
        i = 0
        while (imp := ctx.importDecl(i)) is not None:
            i += 1
            imports.append(imp.accept(self))
        return File(imports)

    def visitImportWithAlias(self, ctx: HerbParser.ImportWithAliasContext):
        alias = str(ctx.IDENT())
        path = ctx.importPath().accept(self)
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias=alias, path=path, is_relative=is_relative, pos=self.pos(ctx))

    def visitImportWithoutAlias(self, ctx: HerbParser.ImportWithoutAliasContext):
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias="", path=path, is_relative=is_relative, pos=self.pos(ctx))

    def visitRelImportPath(self, ctx: HerbParser.RelImportPathContext) -> Tuple[bool, Tuple[str]]:
        path = []
        i = 0
        while (id := ctx.IDENT(i)) is not None:
            i += 1
            path.append(str(id))
        return True, tuple(path)

    def visitAbsImportPath(self, ctx: HerbParser.AbsImportPathContext) -> Tuple[bool, Tuple[str]]:
        path = []
        i = 0
        while (id := ctx.IDENT(i)) is not None:
            i += 1
            path.append(str(id))
        return False, tuple(path)

    def pos(self, ctx: ParserRuleContext):
        return Pos(filepath=self.filepath, line=ctx.start.line, column=ctx.start.column)
