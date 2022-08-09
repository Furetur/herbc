from typing import cast

from src.ast import Module, AstVisitor, VarDecl, IdentExpr
from src.context.compilation_ctx import CompilationCtx


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor()
    mod.accept(v, None)


class TypeCheckVisitor(AstVisitor):

    def visit_node(self, n, data):
        n.accept_children(self, None)

    def visit_var_decl(self, v: 'VarDecl', data):
        v.initializer.accept(self, None)
        v.ty = v.initializer.ty

    def visit_ident_expr(self, i: 'IdentExpr', data):
        assert i.decl is not None
        assert type(i.decl) is VarDecl
        i.ty = cast(VarDecl, i.decl).ty
