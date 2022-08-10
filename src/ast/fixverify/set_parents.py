from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ast import Module, Node

from src.ast.visitors import AstVisitor


def set_parents(mod: 'Module'):
    # module has no parent
    mod.accept(SetParentsVisitor(), None)


class SetParentsVisitor(AstVisitor['Node', None]):
    def visit_node(self, n: 'Node', data: 'Node'):
        # 'data' --- parent of 'n'
        n.parent = data
        n.accept_children(self, n)
