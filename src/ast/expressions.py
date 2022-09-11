from enum import Enum
from typing import List, TYPE_CHECKING, Union

from src.ast.base import Expr
from src.ast.utils import fancy_pos

if TYPE_CHECKING:
    from src.ast import AstVisitor, AstTransformer, D, R, Decl


class FunCall(Expr):
    name: str
    args: List[Expr]

    def __init__(self, *, name: str, args: List[Expr], **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.args = args

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_fun_call(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        for arg in self.args:
            arg.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        for i in range(len(self.args)):
            self.args[i] = self.args[i].accept(transformer, data)

    def __str__(self):
        args = ", ".join(str(e) for e in self.args)
        return f"{self.name}({args})"


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
    LESS = '<'


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
