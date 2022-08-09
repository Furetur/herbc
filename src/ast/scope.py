from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from src.ast.base import Decl


class Scope:
    __declarations: Dict[str, 'Decl']

    def __init__(self):
        self.__declarations = dict()

    def __contains__(self, name: str):
        return name in self.__declarations

    def declare(self, decl: 'Decl'):
        assert decl.declared_name() not in self
        self.__declarations[decl.declared_name()] = decl

    def get_declaration(self, name: str) -> 'Decl':
        assert name in self
        return self.__declarations[name]
