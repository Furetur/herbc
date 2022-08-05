from typing import cast, Dict

from src.ast import Module, AstVisitor, IntLiteral, Node, VarDecl, IdentExpr, Decl
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyInt


def evaluate(ctx: CompilationCtx, m: Module):
    v = EvaluateVisitor()
    v.visit(m)


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
