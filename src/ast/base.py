from abc import abstractmethod, ABC
from typing import Union, TypeVar, TYPE_CHECKING

from src.span import Span
from src.ty import Ty, TyUnknown
from src.ast.visitors import AstVisitor, AstTransformer

D = TypeVar('D')
R = TypeVar('R')


__node_id = -1


def next_node_id() -> int:
    global __node_id
    __node_id += 1
    return __node_id


class Node(ABC):
    id: int
    span: Span
    parent: Union['Node', None]

    def __init__(self, *, span: Span, parent: Union['Node', None] = None):
        self.id = next_node_id()
        self.span = span
        self.parent = parent

    @abstractmethod
    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R': ...

    @abstractmethod
    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'): ...

    @abstractmethod
    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'): ...

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id

    def __hash__(self):
        return self.id


class Expr(Node, ABC):
    ty: Ty

    def __init__(self, *, ty: Ty = TyUnknown, **kwargs):
        super().__init__(**kwargs)
        self.ty = ty


class Stmt(Node, ABC):
    ...


class Decl(Stmt, ABC):
    @abstractmethod
    def declared_name(self) -> str: ...


class RValueDecl(Decl, ABC):
    @abstractmethod
    def value_ty(self) -> Ty: ...
