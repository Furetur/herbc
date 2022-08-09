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