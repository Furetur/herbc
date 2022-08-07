from typing import cast

from src.ast import Module, AstVisitor, VarDecl, IdentExpr
from src.context.compilation_ctx import CompilationCtx


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor()
    v.visit(mod)


class TypeCheckVisitor(AstVisitor):
    def visit_var_decl(self, v: 'VarDecl'):
        self.visit(v.initializer)
        v.ty = v.initializer.ty

    def visit_ident_expr(self, i: 'IdentExpr'):
        assert i.decl is not None
        assert type(i.decl) is VarDecl
        i.ty = cast(VarDecl, i.decl).ty
