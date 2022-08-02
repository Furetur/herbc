from pathlib import Path
from typing import Tuple


from src.ast import Import, Module, Stmt, FunDecl, ExprStmt, IntLiteral, FunCall, Expr, Decl
from src.span import Span, INVALID_SPAN
from src.parser.generated.HerbParser import HerbParser
from src.parser.generated.HerbVisitor import HerbVisitor
from src.ty import TyInt


class HerbParserVisitor(HerbVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def visitProg(self, ctx: HerbParser.ProgContext) -> Module:
        mod = Module(imports=[], declarations=[], path=self.filepath, span=Span(0, 0), parent=None)
        # imports
        i = 0
        while (impCtx := ctx.importDecl(i)) is not None:
            i += 1
            imp: Import = impCtx.accept(self)
            imp.parent = mod
            mod.imports.append(imp)
        # declarations
        i = 0
        while (declCtx := ctx.funcDecl(i)) is not None:
            i += 1
            decl: Decl = self.visit(declCtx)
            decl.parent = mod
            mod.declarations.append(decl)
        return mod

    # ===== DECLARATIONS =====
    def visitImportWithAlias(self, ctx: HerbParser.ImportWithAliasContext):
        alias = str(ctx.IDENT())
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias=alias, path=path, is_relative=is_relative, span=Span.from_antlr(ctx), parent=None)

    def visitImportWithoutAlias(self, ctx: HerbParser.ImportWithoutAliasContext):
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias="", path=path, is_relative=is_relative, span=Span.from_antlr(ctx), parent=None)

    def visitFuncDecl(self, ctx:HerbParser.FuncDeclContext):
        name = str(ctx.IDENT())

        fun_decl = FunDecl(name=name, body=[], parent=None, span=Span.from_antlr(ctx))

        i = 0
        while (stmtCtx := ctx.stmt(i)) is not None:
            i += 1
            stmt: Stmt = self.visit(stmtCtx)
            stmt.parent = fun_decl
            fun_decl.body.append(stmt)

        return fun_decl

    # ===== EXPRESSIONS =====

    def visitIntLit(self, ctx:HerbParser.IntLitContext):
        value = int(ctx.getText())
        return IntLiteral(value=value, parent=None, span=Span.from_antlr(ctx), ty=TyInt)

    def visitFunCall(self, ctx:HerbParser.FunCallContext):
        name = str(ctx.IDENT())
        assert name == "print", "unimplemented: can only call 'print' function"
        call = FunCall(fn_name=name, args=[], parent=None, span=Span.from_antlr(ctx), ty=TyInt)
        for arg in self.visit(ctx.commaSeparatedExprs()):
            arg: Expr
            arg.parent = call
            call.args.append(arg)
        return call

    # ===== STATEMENTS =====

    def visitExprStmt(self, ctx:HerbParser.ExprStmtContext):
        expr = self.visit(ctx.expr())
        return ExprStmt(expr=expr, parent=None, span=Span.from_antlr(ctx))

    # ===== UTIL =====

    def visitCommaSeparatedExprs(self, ctx:HerbParser.CommaSeparatedExprsContext):
        exprs = []
        i = 0
        while (exprCtx := ctx.expr(i)) is not None:
            i += 1
            expr = self.visit(exprCtx)
            exprs.append(expr)
        return exprs

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
