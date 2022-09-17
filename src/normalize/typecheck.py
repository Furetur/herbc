from typing import cast

from src.ast import Module, VarDecl, IdentExpr, AstWalker, AssignStmt, BinopKind, Expr, BinopExpr, IfStmt, WhileStmt, \
    UnopKind, UnopExpr, RValueDecl, ArgDecl
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyUnknown, TyInt, Ty, TyBool, TyVoid


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor(ctx)
    v.walk(mod)


# (operand_type, result_type)
binop_types = {
    BinopKind.PLUS: (TyInt, TyInt),
    BinopKind.MINUS: (TyInt, TyInt),
    BinopKind.MUL: (TyInt, TyInt),
    BinopKind.DIV: (TyInt, TyInt),
    BinopKind.MOD: (TyInt, TyInt),
    BinopKind.BITWISE_OR: (TyInt, TyInt),
    BinopKind.BITWISE_AND: (TyInt, TyInt),

    BinopKind.LT: (TyInt, TyBool),
    BinopKind.LTE: (TyInt, TyBool),
    BinopKind.EQ: (TyInt, TyBool),
    BinopKind.NEQ: (TyInt, TyBool),
    BinopKind.GT: (TyInt, TyBool),
    BinopKind.GTE: (TyInt, TyBool),
    BinopKind.LOGICAL_AND: (TyBool, TyBool),
    BinopKind.LOGICAL_OR: (TyBool, TyBool),
}

# (operand_type, result_type)
unop_types = {
    UnopKind.MINUS: (TyInt, TyInt),
    UnopKind.BANG: (TyBool, TyBool)
}


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

    def walk_arg_decl(self, n: 'ArgDecl'):
        if n.value_ty() == TyVoid:
            self.ctx.add_error_to_node(
                node=n,
                message=f"Cannot use 'void' as a formal argument type",
                hint="void can only be used as the return type"
            )

    def walk_var_decl(self, v: 'VarDecl'):
        v.initializer.accept(self, None)
        v.ty = v.initializer.ty

    def walk_ident_expr(self, i: 'IdentExpr'):
        assert i.decl is not None
        assert isinstance(i.decl, RValueDecl)
        i.ty = cast(RValueDecl, i.decl).value_ty()

    def walk_binop(self, n: 'BinopExpr'):
        super(TypeCheckVisitor, self).walk_binop(n)
        assert n.kind in binop_types
        operand_ty, result_ty = binop_types[n.kind]
        hint = f"Binary '{n.kind.value}' operator is only supported for '{operand_ty}' types"
        self.require_type(n.left, operand_ty, hint)
        self.require_type(n.right, operand_ty, hint)
        n.ty = result_ty

    def walk_unop(self, n: 'UnopExpr'):
        super().walk_unop(n)
        assert n.kind in unop_types
        operand_ty, result_ty = unop_types[n.kind]
        hint = f"Unary '{n.kind.value}' operator is supported only for '{operand_ty}' types"
        self.require_type(n.expr, operand_ty, hint)
        n.ty = result_ty

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

    def walk_while_stmt(self, n: 'WhileStmt'):
        super().walk_while_stmt(n)
        self.require_type(n.cond, TyBool, "While conditions must be of type 'bool'")
