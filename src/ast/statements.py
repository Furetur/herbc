from src.ast.base import Stmt

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ast import Expr, AstVisitor, D, R, AstTransformer


class ExprStmt(Stmt):
    expr: 'Expr'

    def __init__(self, *, expr: 'Expr', **kwargs):
        super().__init__(**kwargs)
        self.expr = expr

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_expr_stmt(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        self.expr.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        self.expr = self.expr.accept(transformer, data)

    def __str__(self):
        return f"{self.expr};"
