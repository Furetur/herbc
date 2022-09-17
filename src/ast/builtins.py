from typing import TYPE_CHECKING, TypeVar

from src.span import INVALID_SPAN
from src.ty import TyVoid

from src.ast.declarations import BuiltinDecl
from src.ast.base import Expr
from src.ast.visitors import AstTransformer, AstVisitor


D = TypeVar("D")
R = TypeVar("R")


PrintBuiltinDecl = BuiltinDecl(
    name="print",
    span=INVALID_SPAN
)

builtin_declarations = [PrintBuiltinDecl]


class Print(Expr):
    arg: Expr

    def __init__(self, *, arg: Expr, **kwargs):
        super(Print, self).__init__(ty=TyVoid, **kwargs)
        self.arg = arg

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_print(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        self.arg.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        self.arg = self.arg.accept(transformer, data)

    def __str__(self):
        return f"print({self.arg})"
