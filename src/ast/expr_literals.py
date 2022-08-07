import dataclasses

from src.ast.nodes import Expr, AstVisitor, Node
from src.ty import TyInt, TyBool


@dataclasses.dataclass(kw_only=True)
class Literal(Expr):
    pass


@dataclasses.dataclass(kw_only=True)
class IntLiteral(Literal):
    ty = TyInt
    value: int

    def accept(self, visitor: AstVisitor):
        return visitor.visit_int_literal(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert False

    def __str__(self):
        return f"{self.value} as {self.ty}"


@dataclasses.dataclass(kw_only=True)
class BoolLiteral(Literal):
    ty = TyBool
    value: bool

    def accept(self, visitor: AstVisitor):
        return visitor.visit_bool_literal(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert False

    def __str__(self):
        v = "true" if self.value else "false"
        return f"{v} as bool"
