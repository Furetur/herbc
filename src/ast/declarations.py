from typing import TYPE_CHECKING, Tuple, Union, List
from pathlib import Path

if TYPE_CHECKING:
    from src.ast import Node, Module
    from src.ast.visitors import D, R

from src.ty import Ty, TyUnknown
from src.ast.visitors import *
from src.ast.base import Decl
from src.ast.scope import Scope

class Import(Decl):
    alias: str
    imported_module: Union['Module', None]

    def __init__(self, *, alias: str, path: Tuple[str], is_relative: bool, **kwargs):
        super().__init__(**kwargs)
        self.alias: str = alias
        self.path: Tuple[str] = path
        self.is_relative: bool = is_relative
        self.imported_module = None

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_import(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        pass

    def transform_children(self, transformer: AstTransformer[D], data: D):
        pass

    def declared_name(self) -> str:
        assert len(self.path) > 0
        return self.alias if self.alias != "" else self.path[-1]

    def has_alias(self) -> bool:
        return self.alias != ""

    def import_path(self) -> str:
        if self.is_relative:
            return "." + ".".join(self.path)
        else:
            return ".".join(self.path)

    def resolved_path(self) -> Path:
        assert self.imported_module is not None
        return self.imported_module.path

    def __str__(self):
        return f"import {self.declared_name()} = {self.import_path()};"


class FunDecl(Decl, Scope):
    name: str
    body: 'StmtSeq'

    def __init__(self, *, name: str, body: 'StmtSeq', **kwargs):
        Decl.__init__(self, **kwargs)
        Scope.__init__(self)
        self.name = name
        self.body = body

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_fun_decl(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        self.body.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        self.body = self.body.accept(transformer, data)

    def declared_name(self) -> str:
        return self.name

    def __str__(self):
        return f"fn {self.name} () {self.body}"


class VarDecl(Decl):
    name: str
    ty: 'Ty'
    initializer: Union['Expr', None]

    def __init__(self, *, name: str, initializer: Union['Expr', None], ty: Ty = TyUnknown, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.ty = ty
        self.initializer = initializer

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_var_decl(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        self.initializer.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        self.initializer = self.initializer.accept(transformer, data)

    def declared_name(self) -> str:
        return self.name

    def name(self) -> str:
        return self.name

    def __str__(self):
        return f"const {self.name}: {self.ty or '?'} = {self.initializer};"
