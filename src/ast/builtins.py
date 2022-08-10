from typing import TYPE_CHECKING, TypeVar

from src.ty import TyVoid

if TYPE_CHECKING:
    pass
from src.ast.base import Expr
from src.ast.visitors import AstTransformer, AstVisitor


D = TypeVar("D")
R = TypeVar("R")


class PrintInt(Expr):
    arg: Expr

    def __init__(self, *, arg: Expr, **kwargs):
        super().__init__(ty=TyVoid, **kwargs)
        self.arg = arg

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_print_int(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        self.arg.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        self.arg = self.arg.accept(transformer, data)

    def __str__(self):
        return f"print_int({self.arg})"


class PrintBool(Expr):
    arg: Expr

    def __init__(self, *, arg: Expr, **kwargs):
        super().__init__(ty=TyVoid, **kwargs)
        self.arg = arg

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_print_bool(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        self.arg.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        self.arg = self.arg.accept(transformer, data)

    def __str__(self):
        return f"print_bool({self.arg})"


class PrintStr(Expr):
    arg: Expr

    def __init__(self, *, arg: Expr, **kwargs):
        super().__init__(ty=TyVoid, **kwargs)
        self.arg = arg

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_print_str(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        self.arg.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        self.arg = self.arg.accept(transformer, data)

    def __str__(self):
        return f"print_str({self.arg})"
