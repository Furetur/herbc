from typing import TYPE_CHECKING, TypeVar, Generic
from src.ast.visitors import AstVisitor

if TYPE_CHECKING:
    from src.ast import *

D = TypeVar("D")


class AstTransformer(AstVisitor['Node', D], Generic[D]):
    def visit_node(self, n: 'Node', data: D) -> 'Node':
        n.transform_children(self, data)
        return n
