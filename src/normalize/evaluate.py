from typing import cast, Dict

from src.ast import Module, AstVisitor, IntLiteral, Node, VarDecl, IdentExpr, Decl
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.ty import TyInt


def evaluate(ctx: CompilationCtx, m: Module):
    c = CheckConstants(ctx)
    c.visit(m)
    if ctx.has_errors():
        raise CompilationInterrupted()
    v = EvaluateVisitor()
    v.visit(m)
    if ctx.has_errors():
        raise CompilationInterrupted()


class CheckConstants(AstVisitor):
    """
    Check "const a = expr;" declarations
    """
    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    def visit_var_decl(self, v: 'VarDecl'):
        if type(v.initializer) is not IntLiteral and type(v.initializer) is not IdentExpr:
            self.ctx.add_error_to_node(
                v,
                message="Only literals and identifiers are allowed in const declarations",
                hint=f"expression at '{v.initializer.human_readable_position()}' is not a literal or an identifier"
            )


class EvaluateVisitor(AstVisitor):
    evaluated: Dict[Decl, Node]

    def __init__(self):
        self.evaluated = dict()

    def visit_ident_expr(self, i: 'IdentExpr') -> Node:
        decl = cast(VarDecl, i.decl)
        assert decl is not None and type(decl) is VarDecl
        initializer = cast(IntLiteral, decl.initializer)
        assert type(initializer) is IntLiteral
        i.parent.swap_child(old=i, new=IntLiteral(value=initializer.value, span=i.span, parent=None, ty=TyInt))
