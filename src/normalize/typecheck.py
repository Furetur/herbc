from typing import cast

from src.ast import Module, VarDecl, IdentExpr, AstWalker
from src.context.compilation_ctx import CompilationCtx


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor()
    v.walk(mod)


class TypeCheckVisitor(AstWalker):
    def walk_var_decl(self, v: 'VarDecl'):
        v.initializer.accept(self, None)
        v.ty = v.initializer.ty

    def walk_ident_expr(self, i: 'IdentExpr'):
        assert i.decl is not None
        assert type(i.decl) is VarDecl
        i.ty = cast(VarDecl, i.decl).ty
