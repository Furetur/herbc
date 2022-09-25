from typing import cast

from src.ast import Module, VarDecl, IdentExpr, AstWalker, AssignStmt, BinopKind, Expr, BinopExpr, IfStmt, WhileStmt, \
    UnopKind, UnopExpr, RValueDecl, ArgDecl, FunCall, ExprStmt, Print, RetStmt, FunDecl
from src.ast.utils import first_ancestor_of_type
from src.context.compilation_ctx import CompilationCtx
from src.normalize.function_termination_check import FunctionTerminationChecker
from src.ty import TyUnknown, TyInt, Ty, TyBool, TyVoid, TyFunc, TyBuiltin, TyStr


def typecheck(ctx: CompilationCtx, mod: Module):
    v = TypeCheckVisitor(ctx)
    v.walk(mod)
    v = FunctionTerminationChecker(ctx)
    v.visit(mod, None)


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
        if i.ty == TyBuiltin:
            self.ctx.add_error_to_node(
                node=i,
                message="Cannot use a builtin as a value",
                hint="You can only call a builtin, you cannot store it anywhere"
            )

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

    def walk_fun_call(self, n: 'FunCall'):
        super().walk_fun_call(n)
        assert n.callee.ty is not None
        if not isinstance(n.callee.ty, TyFunc):
            self.ctx.add_error_to_node(
                node=n,
                message=f"Type '{n.callee.ty}' is not a function",
                hint="You can only call functions"
            )
        elif len(n.args) != len(n.callee.ty.args):
            self.ctx.add_error_to_node(
                node=n,
                message=f"Expected {len(n.callee.ty.args)} arguments but received {len(n.args)}",
            )
        else:
            for formal_arg, arg in zip(n.callee.ty.args, n.args):
                self.require_type(arg, formal_arg, hint="Invalid argument type")
            n.ty = n.callee.ty.ret
        if n.ty == TyVoid and not isinstance(n.parent, ExprStmt):
            self.ctx.add_error_to_node(
                node=n,
                message="This call returns 'void', it cannot be used as a value"
            )

    def walk_assign_stmt(self, n: 'AssignStmt'):
        # calculate types and check lvalue
        self.walk(n.rvalue)
        if not isinstance(n.lvalue, IdentExpr) or not isinstance(n.lvalue.decl, VarDecl):
            self.ctx.add_error_to_node(
                node=n.lvalue,
                message="Expected a variable on the left-hand side"
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

    def walk_print(self, n: 'Print'):
        super().walk_print(n)
        if n.arg.ty not in [TyInt, TyBool, TyStr]:
            self.ctx.add_error_to_node(
                node=n,
                message=f"Cannot print value of type '{n.arg.ty}'",
            )

    def walk_ret(self, n: 'RetStmt'):
        super().walk_ret(n)
        fn = cast(FunDecl, first_ancestor_of_type(n, FunDecl))
        if fn is None:
            self.ctx.add_error_to_node(
                node=n,
                message="'return' statements can only be used inside functions"
            )
            return
        expr_ty = n.expr.ty if n.expr is not None else TyVoid
        if expr_ty != fn.ret_ty:
            self.ctx.add_error_to_node(
                node=n,
                message=f"Expected type '{fn.ret_ty}', but received '{expr_ty}'",
                hint="The return statement has a value of incorrect type"
            )
