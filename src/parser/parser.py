from pathlib import Path
from typing import Tuple


from src.ast import Import, Module
from src.span import Span, INVALID_SPAN
from src.parser.generated.HerbParser import HerbParser
from src.parser.generated.HerbVisitor import HerbVisitor





class HerbParserVisitor(HerbVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def visitProg(self, ctx: HerbParser.ProgContext) -> Module:
        imports = []
        i = 0
        while (imp := ctx.importDecl(i)) is not None:
            i += 1
            imports.append(imp.accept(self))
        mod = Module(imports=imports, path=self.filepath, span=INVALID_SPAN, parent=None)
        for i in imports:
            i.parent = mod
        return mod

    def visitImportWithAlias(self, ctx: HerbParser.ImportWithAliasContext):
        alias = str(ctx.IDENT())
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias=alias, path=path, is_relative=is_relative, span=Span.from_antlr(ctx), parent=None)

    def visitImportWithoutAlias(self, ctx: HerbParser.ImportWithoutAliasContext):
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias="", path=path, is_relative=is_relative, span=Span.from_antlr(ctx), parent=None)

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
