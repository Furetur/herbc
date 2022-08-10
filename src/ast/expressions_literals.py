from typing import TYPE_CHECKING
from abc import ABC
if TYPE_CHECKING:
    from src.ast import *

from src.ast.base import Expr
from src.ty import TyInt, TyBool, TyStr


class Literal(Expr, ABC):
    pass


class IntLiteral(Literal):
    value: int

    def __init__(self, *, value: int, **kwargs):
        super().__init__(ty=TyInt, **kwargs)
        self.value = value

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_int_literal(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        pass

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        pass

    def __str__(self):
        return f"{self.value} as {self.ty}"


class BoolLiteral(Literal):
    value: bool

    def __init__(self, *, value: bool, **kwargs):
        super().__init__(ty=TyBool, **kwargs)
        self.value = value

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_bool_literal(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        pass

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        pass

    def __str__(self):
        v = "true" if self.value else "false"
        return f"{v} as bool"


class StrLiteral(Literal):
    value: str

    def __init__(self, *, value: str, **kwargs):
        super().__init__(ty=TyStr, **kwargs)
        self.value = value

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_str_literal(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        pass

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        pass
