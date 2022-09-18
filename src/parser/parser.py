from pathlib import Path
from typing import Tuple

from src.ast import Import, Module, Stmt, FunDecl, ExprStmt, IntLiteral, FunCall, Expr, Decl, VarDecl, Scope, IdentExpr, \
    BoolLiteral, StrLiteral, AssignStmt, BinopExpr, BinopKind, StmtBlock, IfStmt, WhileStmt, UnopExpr, UnopKind, \
    ArgDecl, RetStmt
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationError
from src.span import Span, INVALID_SPAN
from src.parser.generated.HerbParser import HerbParser
from src.parser.generated.HerbVisitor import HerbVisitor
from src.ty import TyInt, TyUnknown, TyBool, ty_primitive_by_name, Ty, TyFunc, TyVoid


def get_all(get, start_i=0):
    result = []
    i = start_i
    while (ctx := get(i)) is not None:
        i += 1
        result.append(ctx)
    return result


class HerbParserVisitor(HerbVisitor):
    def __init__(self, filepath: Path, compiler: CompilationCtx):
        self.filepath = filepath
        self.compiler = compiler

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
            args=[self.visit(arg) for arg in get_all(lambda i: ctx.argDecl(i))],
            body=self.visitBlock(ctx.block()),
            ret_ty=self.visit(ctx.typ()) if ctx.typ() is not None else TyVoid,
            span=Span.from_antlr(ctx)
        )

    def visitArgDecl(self, ctx:HerbParser.ArgDeclContext):
        return ArgDecl(
            name=str(ctx.IDENT()),
            ty=self.visit(ctx.typ()),
            span=Span.from_antlr(ctx)
        )

    def visitVarDecl(self, ctx: HerbParser.VarDeclContext):
        return VarDecl(
            name=str(ctx.IDENT()),
            initializer=self.visit(ctx.expr()),
            span=Span.from_antlr(ctx),
        )

    # ===== EXPRESSIONS =====

    def visitParenExpr(self, ctx:HerbParser.ParenExprContext):
        return self.visit(ctx.expr())

    def visitBinopExpr(self, ctx:HerbParser.BinopExprContext):
        return BinopExpr(
            left=self.visit(ctx.expr(0)),
            right=self.visit(ctx.expr(1)),
            kind=BinopKind(ctx.op.text),
            span=Span.from_antlr(ctx)
        )

    def visitUnaryopExpr(self, ctx:HerbParser.UnaryopExprContext):
        return UnopExpr(
            expr=self.visit(ctx.expr()),
            kind=UnopKind(ctx.op.text),
            span=Span.from_antlr(ctx)
        )

    def visitIntLit(self, ctx: HerbParser.IntLitContext):
        return IntLiteral(value=int(ctx.getText()), span=Span.from_antlr(ctx))

    def visitBoolLit(self, ctx: HerbParser.BoolLitContext):
        text = ctx.getText()
        assert text in ["true", "false"]
        return BoolLiteral(value=(text == "true"), span=Span.from_antlr(ctx))

    def visitStrLit(self, ctx: HerbParser.StrLitContext):
        text = ctx.getText()[1:-1]
        return StrLiteral(value=text, span=Span.from_antlr(ctx))

    def visitFunCall(self, ctx: HerbParser.FunCallContext):
        return FunCall(
            callee=self.visit(ctx.callee),
            args=[arg for arg in self.visit(ctx.commaSeparatedExprs())] if ctx.commaSeparatedExprs() is not None else [],
            span=Span.from_antlr(ctx),
        )

    def visitReference(self, ctx: HerbParser.ReferenceContext):
        return IdentExpr(name=str(ctx.IDENT()), span=Span.from_antlr(ctx))

    # ===== STATEMENTS =====

    def visitBlock(self, ctx: HerbParser.BlockContext) -> StmtBlock:
        statements = []
        i = 0
        while (stmtCtx := ctx.stmt(i)) is not None:
            i += 1
            statements.append(self.visit(stmtCtx))
        return StmtBlock(stmts=statements, span=Span.from_antlr(ctx))

    def visitExprStmt(self, ctx: HerbParser.ExprStmtContext):
        return ExprStmt(expr=self.visit(ctx.expr()), span=Span.from_antlr(ctx))

    def visitAssign(self, ctx: HerbParser.AssignContext):
        return AssignStmt(lvalue=self.visit(ctx.expr(0)), rvalue=self.visit(ctx.expr(1)), span=Span.from_antlr(ctx))

    def visitIfStmt(self, ctx: HerbParser.IfStmtContext) -> IfStmt:
        cond_branch = (self.visit(ctx.expr()), self.visit(ctx.thenBlock))
        if ctx.elseBlock is not None:
            return IfStmt(
                condition_branches=[cond_branch],
                else_branch=self.visit(ctx.elseBlock),
                span=Span.from_antlr(ctx)
            )
        elif ctx.elseIf is not None:
            else_if: IfStmt = self.visitIfStmt(ctx.elseIf)
            return IfStmt(
                condition_branches=[cond_branch] + else_if.condition_branches,
                else_branch=else_if.else_branch,
                span=Span.from_antlr(ctx)
            )
        else:
            return IfStmt(
                condition_branches=[cond_branch],
                else_branch=None,
                span=Span.from_antlr(ctx)
            )

    def visitWhileStmt(self, ctx:HerbParser.WhileStmtContext):
        return WhileStmt(
            cond=self.visit(ctx.expr()),
            body=self.visit(ctx.block()),
            span=Span.from_antlr(ctx)
        )

    def visitRetStmt(self, ctx:HerbParser.RetStmtContext):
        return RetStmt(
            expr=self.visit(ctx.expr()) if ctx.expr() is not None else None,
            span=Span.from_antlr(ctx)
        )

    # ===== TYPES =====

    def visitTypLit(self, ctx:HerbParser.TypLitContext) -> 'Ty':
        text = ctx.getText()
        if text in ty_primitive_by_name:
            return ty_primitive_by_name[text]
        else:
            allowed_types = ', '.join(str(ty) for ty in ty_primitive_by_name.values())
            self.compiler.add_error(CompilationError(
                filepath=self.filepath,
                message=f"Unknown type '{text}'",
                hint=f"Allowed types: {allowed_types}.",
                span=Span.from_antlr(ctx)
            ))

    def visitTypFunc(self, ctx:HerbParser.TypFuncContext):
        types = [self.visit(ty) for ty in get_all(lambda i: ctx.typ(i))]
        assert len(types) > 1
        return TyFunc(args=types[:-1], ret=types[-1])

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
