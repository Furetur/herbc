import dataclasses
from typing import cast

from src.ast import Expr, Node
from src.ast.visitor import AstVisitor


@dataclasses.dataclass(kw_only=True)
class PrintInt(Expr):
    arg: Expr

    def accept(self, visitor: AstVisitor):
        visitor.visit_print_int(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert self.arg is old
        assert isinstance(new, Expr)
        self.arg = cast(Expr, new)
        new.parent = self

    def __str__(self):
        return f"print_int({self.arg})"


@dataclasses.dataclass(kw_only=True)
class PrintBool(Expr):
    arg: Expr

    def accept(self, visitor: AstVisitor):
        visitor.visit_print_bool(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert self.arg is old
        assert isinstance(new, Expr)
        self.arg = cast(Expr, new)
        new.parent = self

    def __str__(self):
        return f"print_bool({self.arg})"
