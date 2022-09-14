from pathlib import Path
from typing import Tuple

from src.ast import Import, Module, Stmt, FunDecl, ExprStmt, IntLiteral, FunCall, Expr, Decl, VarDecl, Scope, IdentExpr, \
    BoolLiteral, StrLiteral, AssignStmt, BinopExpr, BinopKind, StmtBlock
from src.span import Span, INVALID_SPAN
from src.parser.generated.HerbParser import HerbParser
from src.parser.generated.HerbVisitor import HerbVisitor
from src.ty import TyInt, TyUnknown, TyBool


class HerbParserVisitor(HerbVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def visitProg(self, ctx: HerbParser.ProgContext) -> Module:
        # imports
        imports = []
        i = 0
        while (impCtx := ctx.importDecl(i)) is not None:
            i += 1
            imp: Import = impCtx.accept(self)
            imports.append(imp)
        # declarations
        declarations = []
        i = 0
        while (declCtx := ctx.topLevelDecl(i)) is not None:
            i += 1
            decl: Decl = self.visit(declCtx)
            declarations.append(decl)
        return Module(imports=imports, top_level_decls=declarations, path=self.filepath, span=Span(0, 0))

    # ===== DECLARATIONS =====
    def visitImportWithAlias(self, ctx: HerbParser.ImportWithAliasContext):
        alias = str(ctx.IDENT())
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias=alias, path=path, is_relative=is_relative, span=Span.from_antlr(ctx))

    def visitImportWithoutAlias(self, ctx: HerbParser.ImportWithoutAliasContext):
        is_relative, path = ctx.importPath().accept(self)
        return Import(alias="", path=path, is_relative=is_relative, span=Span.from_antlr(ctx))

    def visitFuncDecl(self, ctx: HerbParser.FuncDeclContext):
        return FunDecl(
            name=str(ctx.IDENT()),
            body=self.visitBlock(ctx.block()),
            span=Span.from_antlr(ctx)
        )

    def visitVarDecl(self, ctx: HerbParser.VarDeclContext):
        return VarDecl(
            name=str(ctx.IDENT()),
            initializer=self.visit(ctx.expr()),
            span=Span.from_antlr(ctx),
        )

    # ===== EXPRESSIONS =====

    def visitAdditiveBinopExpr(self, ctx:HerbParser.AdditiveBinopExprContext):
        return BinopExpr(
            left=self.visit(ctx.expr(0)),
            right=self.visit(ctx.expr(1)),
            kind=BinopKind.PLUS,
            span=Span.from_antlr(ctx)
        )

    def visitLogicalBinopExpr(self, ctx:HerbParser.LogicalBinopExprContext):
        return BinopExpr(
            left=self.visit(ctx.expr(0)),
            right=self.visit(ctx.expr(1)),
            kind=BinopKind.LESS,
            span=Span.from_antlr(ctx)
        )

    def visitIntLit(self, ctx: HerbParser.IntLitContext):
        return IntLiteral(value=int(ctx.getText()), span=Span.from_antlr(ctx))

    def visitBoolLit(self, ctx:HerbParser.BoolLitContext):
        text = ctx.getText()
        assert text in ["true", "false"]
        return BoolLiteral(value=(text == "true"), span=Span.from_antlr(ctx))

    def visitStrLit(self, ctx:HerbParser.StrLitContext):
        text = ctx.getText()[1:-1]
        return StrLiteral(value=text, span=Span.from_antlr(ctx))

    def visitFunCall(self, ctx: HerbParser.FunCallContext):
        name = str(ctx.IDENT())
        assert name == "print", "unimplemented: can only call 'print' function"
        return FunCall(
            name=name,
            args=[arg for arg in self.visit(ctx.commaSeparatedExprs())],
            span=Span.from_antlr(ctx),
        )

    def visitReference(self, ctx: HerbParser.ReferenceContext):
        return IdentExpr(name=str(ctx.IDENT()), span=Span.from_antlr(ctx))

    # ===== STATEMENTS =====

    def visitBlock(self, ctx:HerbParser.BlockContext) -> StmtBlock:
        statements = []
        i = 0
        while (stmtCtx := ctx.stmt(i)) is not None:
            i += 1
            statements.append(self.visit(stmtCtx))
        return StmtBlock(stmts=statements, span=Span.from_antlr(ctx))

    def visitExprStmt(self, ctx: HerbParser.ExprStmtContext):
        return ExprStmt(expr=self.visit(ctx.expr()), span=Span.from_antlr(ctx))

    def visitAssign(self, ctx:HerbParser.AssignContext):
        return AssignStmt(lvalue=self.visit(ctx.expr(0)), rvalue=self.visit(ctx.expr(1)), span=Span.from_antlr(ctx))

    # ===== UTIL =====

    def visitCommaSeparatedExprs(self, ctx: HerbParser.CommaSeparatedExprsContext):
        exprs = []
        i = 0
        while (exprCtx := ctx.expr(i)) is not None:
            i += 1
            exprs.append(self.visit(exprCtx))
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
