from typing import cast

from src.ast import Module, VarDecl, IdentExpr, AstWalker, AssignStmt
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyUnknown


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor(ctx)
    v.walk(mod)


class TypeCheckVisitor(AstWalker):
    ctx: CompilationCtx

    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    def walk_var_decl(self, v: 'VarDecl'):
        v.initializer.accept(self, None)
        v.ty = v.initializer.ty

    def walk_ident_expr(self, i: 'IdentExpr'):
        assert i.decl is not None
        assert type(i.decl) is VarDecl
        i.ty = cast(VarDecl, i.decl).ty

    def walk_assign_stmt(self, n: 'AssignStmt'):
        # calculate types and check lvalue
        self.walk(n.rvalue)
        if not isinstance(n.lvalue, IdentExpr) or not isinstance(n.lvalue.decl, VarDecl):
            self.ctx.add_error_to_node(
                node=n.lvalue,
                message="Expected a variable on the left-hand side",
                hint="You can only assign to variables (identifiers)"
            )
            return
        self.walk(n.lvalue)
        # type check
        left_ty = n.lvalue.ty
        right_ty = n.rvalue.ty
        assert left_ty != TyUnknown and right_ty != TyUnknown, "All types must be known by this point"
        if left_ty != right_ty:
            self.ctx.add_error_to_node(
                node = n.rvalue,
                message=f"Expected type '{left_ty}', but received '{right_ty}'",
                hint=f"The type of the variable {n.lvalue} is '{left_ty}'"
            )
            return
