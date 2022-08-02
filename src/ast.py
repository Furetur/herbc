import dataclasses
from pathlib import Path
from typing import Union, List, Tuple

from src.span import Span
from src.ty import Ty, TyInt


class AstVisitor:
    def visit(self, n: 'Node'):
        return n.accept(self)

    def visit_module(self, m: 'Module'):
        for i in m.imports:
            self.visit(i)
        for d in m.declarations:
            self.visit(d)

    # declarations

    def visit_import(self, i: 'Import'):
        pass

    def visit_fun_decl(self, fn: 'FunDecl'):
        for stmt in fn.body:
            self.visit(stmt)

    # expressions

    def visit_int_literal(self, lit: 'IntLiteral'):
        pass

    def visit_fun_call(self, call: 'FunCall'):
        for expr in call.args:
            self.visit(expr)

    # statements

    def visit_expr_stmt(self, stmt: 'ExprStmt'):
        return self.visit(stmt.expr)


@dataclasses.dataclass(kw_only=True)
class Node:
    span: Span
    parent: Union['Node', None]

    def accept(self, visitor: AstVisitor): ...

    def module(self) -> 'Module':
        if type(self) is Module:
            self: 'Module'
            return self
        else:
            assert self.parent is not None
            return self.parent.module()


@dataclasses.dataclass(kw_only=True)
class Module(Node):
    path: Path
    imports: List['Import']
    declarations: List['Decl']

    def accept(self, visitor: AstVisitor):
        visitor.visit_module(self)

    def name(self) -> str:
        return self.path.stem


@dataclasses.dataclass(kw_only=True)
class Decl(Node):
    pass


@dataclasses.dataclass(kw_only=True)
class Import(Decl):
    alias: str
    path: Tuple[str]
    is_relative: bool

    imported_module: 'Module' = None

    def accept(self, visitor: AstVisitor):
        return visitor.visit_import(self)

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


@dataclasses.dataclass(kw_only=True)
class FunDecl(Decl):
    name: str
    body: List['Stmt']

    def accept(self, visitor: AstVisitor):
        return visitor.visit_fun_decl(self)


@dataclasses.dataclass(kw_only=True)
class Expr(Node):
    ty: Ty


@dataclasses.dataclass(kw_only=True)
class IntLiteral(Expr):
    ty = TyInt
    value: int

    def accept(self, visitor: AstVisitor):
        return visitor.visit_int_literal(self)


@dataclasses.dataclass(kw_only=True)
class FunCall(Expr):
    fn_name: str
    args: List[Expr]

    def accept(self, visitor: AstVisitor):
        return visitor.visit_fun_call(self)


@dataclasses.dataclass(kw_only=True)
class Stmt(Node):
    pass


@dataclasses.dataclass(kw_only=True)
class ExprStmt(Stmt):
    expr: Expr

    def accept(self, visitor: AstVisitor):
        return visitor.visit_expr_stmt(self)
