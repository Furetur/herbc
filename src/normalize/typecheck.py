from typing import cast

from src.ast import Module, VarDecl, IdentExpr, AstWalker, AssignStmt, BinopKind, Expr, BinopExpr, IfStmt
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyUnknown, TyInt, Ty, TyBool


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor(ctx)
    v.walk(mod)


class TypeCheckVisitor(AstWalker):
    ctx: CompilationCtx

    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    # Reusable

    def require_type(self, n: 'Expr', ty: Ty, hint: str = "") -> bool:
        if n.ty != ty:
            self.ctx.add_error_to_node(
                node=n,
                message=f"Expected '{ty}' but received '{n.ty}'",
                hint=hint
            )
            return False
        return True

    # Walker

    def walk_var_decl(self, v: 'VarDecl'):
        v.initializer.accept(self, None)
        v.ty = v.initializer.ty

    def walk_ident_expr(self, i: 'IdentExpr'):
        assert i.decl is not None
        assert type(i.decl) is VarDecl
        i.ty = cast(VarDecl, i.decl).ty

    def walk_binop(self, n: 'BinopExpr'):
        super(TypeCheckVisitor, self).walk_binop(n)
        hint = f"Binary '{n.kind.value}' operator is only supported for integer types"
        self.require_type(n.left, TyInt, hint)
        self.require_type(n.right, TyInt, hint)

        if n.kind == BinopKind.PLUS:
            n.ty = TyInt
        elif n.kind == BinopKind.LESS:
            n.ty = TyBool
        else:
            assert False, "unknown binop kind"

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
        assert left_ty != TyUnknown, "All types must be known by this point"
        self.require_type(n.rvalue, left_ty, f"The type of the variable {n.lvalue} is '{left_ty}'")

    def walk_if_stmt(self, n: 'IfStmt'):
        super().walk_if_stmt(n)
        for cond, _ in n.condition_branches:
            self.require_type(cond, TyBool, "If conditions must be of type 'bool'")
