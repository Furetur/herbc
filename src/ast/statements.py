import dataclasses

from src.ast.base import Stmt

from typing import TYPE_CHECKING, List, Tuple, Dict
from src.ast import Scope

if TYPE_CHECKING:
    from src.ast import Expr, AstVisitor, D, R, AstTransformer


class StmtBlock(Stmt, Scope):
    stmts: 'List[Stmt]'

    def __init__(self, *, stmts: 'List[Stmt]', **kwargs):
        Stmt.__init__(self, **kwargs)
        Scope.__init__(self)
        self.stmts = stmts

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_stmt_block(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        for stmt in self.stmts:
            stmt.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        for i in range(len(self.stmts)):
            self.stmts[i] = self.stmts[i].accept(transformer, data)

    def __str__(self):
        return "{\n" + "\n".join(str(s) for s in self.stmts) + "\n}"


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


class IfStmt(Stmt):
    condition_branches: List[Tuple['Expr', 'StmtBlock']]
    else_branch: StmtBlock | None

    def __init__(self, *, condition_branches: List[Tuple['Expr', 'StmtBlock']], else_branch: StmtBlock | None, **kwargs):
        super().__init__(**kwargs)
        assert len(condition_branches) > 0
        self.condition_branches = condition_branches
        self.else_branch = else_branch

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_if_stmt(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        for cond, block in self.condition_branches:
            cond.accept(visitor, data)
            block.accept(visitor, data)
        if self.else_branch is not None:
            self.else_branch.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        for i in range(len(self.condition_branches)):
            cond, block = self.condition_branches[i]
            self.condition_branches[i] = (cond.accept(transformer, data), block.accept(transformer, data))
        if self.else_branch is not None:
            self.else_branch = self.else_branch.accept(transformer, data)

    def __str__(self):
        result = ""
        # first
        cond, block = self.condition_branches[0]
        result += f"if {cond} {block}"
        # next ones
        for cond, block in self.condition_branches[1:]:
            result += f"else if {cond} {block}"
        return f"if {self.condition_branches[0]}"


class WhileStmt(Stmt):
    cond: 'Expr'
    body: 'StmtBlock'

    def __init__(self, *, cond: 'Expr', body: 'StmtBlock', **kwargs):
        super(WhileStmt, self).__init__(**kwargs)
        self.cond = cond
        self.body = body

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_while_stmt(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        visitor.visit(self.cond, data)
        visitor.visit(self.body, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        self.cond = transformer.visit(self.cond, data)
        self.body = transformer.visit(self.body, data)
