from typing import TYPE_CHECKING, Union

from src.ast import Scope

if TYPE_CHECKING:
    from src.ast.base import Node

from src.ast.module import Module


def module(n: 'Node') -> Module:
    if isinstance(n, Module):
        return n
    else:
        assert n.parent is not None
        return module(n.parent)


def fancy_pos(n: 'Node') -> str:
    mod = module(n)
    return f"{mod.path}:{n.span}"


def is_top_level(n: 'Node') -> bool:
    assert n.parent is not None
    return isinstance(n.parent, Module)


def outerscope(n: 'Node') -> Union[Scope, None]:
    if n.parent is None:
        return None
    elif isinstance(n.parent, Scope):
        return n.parent
    else:
        return outerscope(n.parent)
