from pathlib import Path

from antlr4 import FileStream, CommonTokenStream

from src.ast.declarations import ImportPath, Import
from src.ast.module import File
from src.parser.generated.HerbLexer import HerbLexer
from src.parser.generated.HerbParser import HerbParser
from src.parser.generated.HerbVisitor import HerbVisitor


def parse(path: Path) -> File:
    input_stream = FileStream(str(path))
    lexer = HerbLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = HerbParser(stream)
    tree = parser.prog()
    return tree.accept(HerbParserVisitor())


class HerbParserVisitor(HerbVisitor):
    def visitProg(self, ctx:HerbParser.ProgContext) -> File:
        imports = []
        i = 0
        while (imp := ctx.importDecl(i)) is not None:
            i += 1
            imports.append(imp.accept(self))
        return File(imports)

    def visitImportWithAlias(self, ctx:HerbParser.ImportWithAliasContext):
        alias = str(ctx.IDENT())
        path = ctx.importPath().accept(self)
        return Import(alias, path)

    def visitImportWithoutAlias(self, ctx:HerbParser.ImportWithoutAliasContext):
        path = ctx.importPath().accept(self)
        return Import("", path)

    def visitRelImportPath(self, ctx:HerbParser.RelImportPathContext) -> ImportPath:
        path = []
        i = 0
        while (id := ctx.IDENT(i)) is not None:
            i += 1
            path.append(str(id))
        return ImportPath(is_relative=True, path=tuple(path))

    def visitAbsImportPath(self, ctx:HerbParser.AbsImportPathContext) -> ImportPath:
        path = []
        i = 0
        while (id := ctx.IDENT(i)) is not None:
            i += 1
            path.append(str(id))
        return ImportPath(is_relative=False, path=tuple(path))
