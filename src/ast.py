import dataclasses
from pathlib import Path
from typing import Union, List, Tuple, Dict

from src.span import Span
from src.ty import Ty, TyInt


class AstVisitor:
    def visit(self, n: 'Node'):
        return n.accept(self)

    def visit_module(self, m: 'Module'):
        for i in m.imports:
            self.visit(i)
        for d in m.top_level_decls:
            self.visit(d)

    # declarations

    def visit_import(self, i: 'Import'):
        pass

    def visit_fun_decl(self, fn: 'FunDecl'):
        for stmt in fn.body:
            self.visit(stmt)

    def visit_var_decl(self, v: 'VarDecl'):
        return self.visit(v.initializer)

    # expressions

    def visit_int_literal(self, lit: 'IntLiteral'):
        pass

    def visit_fun_call(self, call: 'FunCall'):
        for expr in call.args:
            self.visit(expr)

    # statements

    def visit_expr_stmt(self, stmt: 'ExprStmt'):
        return self.visit(stmt.expr)

    def visit_ident_expr(self, i: 'IdentExpr'):
        pass


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


# ========= AST =========

@dataclasses.dataclass(kw_only=True)
class Node:
    span: Span
    parent: Union['Node', None]

    def accept(self, visitor: AstVisitor):
        ...

    def swap_child(self, old: 'Node', new: 'Node'):
        ...

    def module(self) -> 'Module':
        if type(self) is Module:
            self: 'Module'
            return self
        else:
            assert self.parent is not None
            return self.parent.module()

    def human_readable_position(self) -> str:
        return f"{self.module().path.name}:{self.span}"


@dataclasses.dataclass(kw_only=True)
class ScopeNode(Node):
    scope: Scope

    def parent_scope(self) -> Union['ScopeNode', None]:
        cur = self.parent
        while cur is not None:
            if isinstance(cur, ScopeNode):
                break
            cur = cur.parent
        return cur


@dataclasses.dataclass(kw_only=True)
class Module(ScopeNode):
    path: Path
    imports: List['Import']
    top_level_decls: List['Decl']

    def accept(self, visitor: AstVisitor):
        visitor.visit_module(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert old in self.imports or old in self.top_level_decls
        new.parent = self
        self.imports = [(i if i is not old else new )for i in self.imports]
        self.top_level_decls = [(d if d is not old else new) for d in self.top_level_decls]

    def name(self) -> str:
        return self.path.stem

    def __str__(self):
        imp = "\n".join([str(i) for i in self.imports])
        decl = "\n".join([str(d) for d in self.top_level_decls])
        return f"// Module {self.path}\n{imp}{decl}"


# === DECLARATIONS ===

@dataclasses.dataclass(kw_only=True)
class Decl(Node):
    def declared_name(self) -> str: ...

    def is_top_level(self) -> bool:
        assert self.parent is not None
        return type(self.parent) is Module


@dataclasses.dataclass(kw_only=True)
class Import(Decl):
    alias: str
    path: Tuple[str]
    is_relative: bool

    imported_module: 'Module' = None

    def accept(self, visitor: AstVisitor):
        return visitor.visit_import(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert False

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


@dataclasses.dataclass(kw_only=True)
class FunDecl(Decl, ScopeNode):
    name: str
    body: List[Node]

    def declared_name(self) -> str:
        return self.name

    def accept(self, visitor: AstVisitor):
        return visitor.visit_fun_decl(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert old in self.body
        new.parent = self
        self.body = [(s if s is not old else new) for s in self.body]

    def __str__(self):
        body = "\n".join(str(n) for n in self.body)
        return f"fn {self.name} () {{{body}}}"


@dataclasses.dataclass(kw_only=True)
class VarDecl(Decl):
    name: str
    ty: Union[Ty, None]
    initializer: Union['Expr', None]

    def accept(self, visitor: AstVisitor):
        return visitor.visit_var_decl(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert old is self.initializer
        new.parent = self
        self.initializer = new

    def declared_name(self) -> str:
        return self.name

    def name(self) -> str:
        return self.name

    def __str__(self):
        return f"const {self.name}: {self.ty or '?'} = {self.initializer};"


# === EXPRESSIONS ===

@dataclasses.dataclass(kw_only=True)
class Expr(Node):
    ty: Ty


@dataclasses.dataclass(kw_only=True)
class IntLiteral(Expr):
    ty = TyInt
    value: int

    def accept(self, visitor: AstVisitor):
        return visitor.visit_int_literal(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert False

    def __str__(self):
        return f"{self.value} as {self.ty}"


@dataclasses.dataclass(kw_only=True)
class FunCall(Expr):
    fn_name: str
    args: List[Expr]

    def accept(self, visitor: AstVisitor):
        return visitor.visit_fun_call(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert old in self.args
        new.parent = self
        self.args = [(e if e is not old else new) for e in self.args]

    def __str__(self):
        args = ", ".join(str(e) for e in self.args)
        return f"{self.fn_name}({args})"


@dataclasses.dataclass(kw_only=True)
class IdentExpr(Expr):
    name: str
    decl: Union[Decl, None] = None

    def accept(self, visitor: AstVisitor):
        return visitor.visit_ident_expr(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert False

    def __str__(self):
        decl = self.decl.human_readable_position() if self.decl is not None else "???"
        return f"{self.name} (declared at '{decl}')"

# === STATEMENTS ===

@dataclasses.dataclass(kw_only=True)
class Stmt(Node):
    pass


@dataclasses.dataclass(kw_only=True)
class ExprStmt(Stmt):
    expr: Expr

    def accept(self, visitor: AstVisitor):
        return visitor.visit_expr_stmt(self)

    def swap_child(self, old: 'Node', new: 'Node'):
        assert old is self.expr
        assert isinstance(new, Expr)
        new.parent = self
        self.expr = new

    def __str__(self):
        return f"{self.expr};"
