from src.ast.base import Stmt

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.ast import Expr, AstVisitor, D, R, AstTransformer


class StmtSeq(Stmt):
    stmts: 'List[Stmt]'

    def __init__(self, *, stmts: 'List[Stmt]', **kwargs):
        super().__init__(**kwargs)
        self.stmts = stmts

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_stmt_seq(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        for stmt in self.stmts:
            stmt.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        for i in range(len(self.stmts)):
            self.stmts[i] = self.stmts[i].accept(transformer, data)


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


class AssignStmt(Stmt):
    lvalue: 'Expr'
    rvalue: 'Expr'

    def __init__(self, *, lvalue: 'Expr', rvalue: 'Expr', **kwargs):
        super(AssignStmt, self).__init__(**kwargs)
        self.lvalue = lvalue
        self.rvalue = rvalue

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_assign_stmt(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        self.lvalue.accept(visitor, data)
        self.rvalue.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        self.lvalue = self.lvalue.accept(transformer, data)
        self.rvalue = self.rvalue.accept(transformer, data)

    def __str__(self):
        return f"{self.lvalue} = {self.rvalue}"
