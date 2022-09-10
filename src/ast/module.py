from pathlib import Path
from typing import List, TYPE_CHECKING

from src.ast.scope import Scope
from src.ast.base import Node

if TYPE_CHECKING:
    from src.ast import Decl, Import, AstVisitor, AstTransformer
    from src.ast.visitors import D, R


class Module(Node, Scope):
    path: Path
    imports: List['Import']
    top_level_decls: List['Decl']

    def __init__(self, *, path: Path, imports: List['Import'], top_level_decls: List['Decl'], **kwargs):
        Node.__init__(self, **kwargs)
        Scope.__init__(self)
        self.path = path
        self.imports = imports
        self.top_level_decls = top_level_decls

    def accept(self, visitor: 'AstVisitor', data: 'D') -> 'R':
        return visitor.visit_module(self, data)

    def accept_children(self, visitor: 'AstVisitor', data: 'D'):
        for i in self.imports:
            visitor.visit_import(i, data)
        for d in self.top_level_decls:
            d.accept(visitor, data)

    def transform_children(self, transformer: 'AstTransformer', data: 'D'):
        for i in range(len(self.imports)):
            self.imports[i] = self.imports[i].accept(transformer, data)
        for i in range(len(self.top_level_decls)):
            self.top_level_decls[i] = self.top_level_decls[i].accept(transformer, data)

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def unique_name(self):
        # TODO: there can be collisions
        return str(hash(self.path)) + "_" + self.name

    def __str__(self):
        decl = "\n".join([str(i) for i in self.declarations])
        return f"// Module {self.path}\n{decl}"
