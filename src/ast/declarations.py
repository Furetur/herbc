from typing import TYPE_CHECKING, Tuple, Union, List
from pathlib import Path

if TYPE_CHECKING:
    from src.ast import Node, Module
    from src.ast.visitors import D, R

from src.ty import *
from src.ast.visitors import *
from src.ast.base import Decl, RValueDecl
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


class FunDecl(RValueDecl, Scope):
    name: str
    args: 'List[ArgDecl]'
    body: 'StmtBlock'
    ret_ty: 'Ty'

    def __init__(self, *, name: str, args: 'List[ArgDecl]', body: 'StmtBlock', ret_ty: 'Ty' = TyVoid, **kwargs):
        Decl.__init__(self, **kwargs)
        Scope.__init__(self)
        self.name = name
        self.args = args
        self.body = body
        self.ret_ty = ret_ty

    def value_ty(self) -> Ty:
        return TyFunc(args=[arg.ty for arg in self.args], ret=self.ret_ty)

    def accept(self, visitor: AstVisitor[D, R], data: D) -> R:
        return visitor.visit_fun_decl(self, data)

    def accept_children(self, visitor: AstVisitor[D, R], data: D):
        for arg in self.args:
            visitor.visit(arg, data)
        self.body.accept(visitor, data)

    def transform_children(self, transformer: AstTransformer[D], data: D):
        for i in range(len(self.args)):
            self.args[i] = transformer.visit(self.args[i], data)
        self.body = self.body.accept(transformer, data)

    def declared_name(self) -> str:
        return self.name

    def __str__(self):
        args = ", ".join(str(arg) for arg in self.args)
        return f"fn {self.name}({args}) {self.body}"


class ArgDecl(RValueDecl):
    name: str
    ty: 'Ty'

    def __init__(self, *, name: str, ty: Ty, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.ty = ty

    def value_ty(self) -> Ty:
        return self.ty

    def declared_name(self) -> str:
        return self.name

    def accept(self, visitor: 'AstVisitor[D, R]', data: 'D') -> 'R':
        return visitor.visit_arg_decl(self, data)

    def accept_children(self, visitor: 'AstVisitor[D, R]', data: 'D'):
        pass

    def transform_children(self, transformer: 'AstTransformer[D]', data: 'D'):
        pass

    def __str__(self):
        return f"{self.name}: {self.ty}"


class VarDecl(RValueDecl):
    name: str
    ty: 'Ty'
    initializer: Union['Expr', None]

    def __init__(self, *, name: str, initializer: Union['Expr', None], ty: Ty = TyUnknown, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.ty = ty
        self.initializer = initializer

    def value_ty(self) -> Ty:
        return self.ty

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
