from enum import Enum
from typing import List, TYPE_CHECKING, Union

from src.ast.base import Expr
from src.ast.utils import fancy_pos

if TYPE_CHECKING:
    from src.ast import AstVisitor, AstTransformer, D, R, Decl


class FunCall(Expr):
    callee: 'Expr'
    args: List[Expr]

    def __init__(self, *, callee: 'Expr', args: List[Expr], **kwargs):
        super().__init__(**kwargs)
        self.callee = callee
        self.args = args

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_fun_call(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        visitor.visit(self.callee, data)
        for arg in self.args:
            arg.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        self.callee = transformer.visit(self.callee, data)
        for i in range(len(self.args)):
            self.args[i] = self.args[i].accept(transformer, data)

    def __str__(self):
        args = ", ".join(str(e) for e in self.args)
        return f"{self.callee}({args})"


class IdentExpr(Expr):
    name: str
    decl: Union['Decl', None] = None

    def __init__(self, *, name: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.decl = None

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_ident_expr(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        pass

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        pass

    def __str__(self):
        decl = fancy_pos(self.decl) if self.decl is not None else "???"
        return f"{self.name} (declared at '{decl}')"


class BinopKind(Enum):
    PLUS = '+'
    MUL = '*'
    DIV = '/'
    MINUS = '-'
    MOD = '%'

    BITWISE_AND = '&'
    BITWISE_OR = '|'

    LT = '<'
    LTE = '<='
    EQ = '=='
    NEQ = '!='
    GT = '>'
    GTE = '>='

    LOGICAL_AND = '&&'
    LOGICAL_OR = '||'


class BinopExpr(Expr):
    left: 'Expr'
    right: 'Expr'
    kind: BinopKind

    def __init__(self, *, left: 'Expr', right: 'Expr', kind: 'BinopKind', **kwargs):
        super(BinopExpr, self).__init__(**kwargs)
        self.left = left
        self.right = right
        self.kind = kind

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_binop(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        self.left.accept(visitor, data)
        self.right.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        self.left = self.left.accept(transformer, data)
        self.right = self.right.accept(transformer, data)

    def __str__(self):
        return f"{self.left} {self.kind.value} {self.right}"


class UnopKind(Enum):
    MINUS = '-'
    BANG = '!'


class UnopExpr(Expr):
    kind: UnopKind
    expr: 'Expr'

    def __init__(self, *, kind: 'UnopKind', expr: 'Expr', **kwargs):
        super(UnopExpr, self).__init__(**kwargs)
        self.kind = kind
        self.expr = expr

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_unop(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        visitor.visit(self.expr, data)

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        self.expr = transformer.visit(self.expr, data)

    def __str__(self):
        return f"{self.kind.value}{self.expr}"