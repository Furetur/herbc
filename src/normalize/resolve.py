from typing import Union, List, cast

from src.ast import Module, AstWalker, Scope, Decl, FunDecl, IdentExpr, VarDecl, Import, FunCall, Node, Literal, \
    StmtBlock, builtin_declarations, Entrypoint, AstTransformer, Expr, DotExpr
from src.ast.fixverify import set_parents
from src.ast.utils import is_top_level, fancy_pos, outerscope
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.ty import TyModule


def resolve(compiler: CompilationCtx, mod: Module):
    reorder_top_level_decls(mod)
    mod.accept(CheckConstants(compiler), None)
    if compiler.has_errors():
        raise CompilationInterrupted()
    v = ResolverTransformer(compiler)
    mod = mod.accept(v, None)
    if compiler.has_errors():
        raise CompilationInterrupted()
    set_parents(mod)
    return mod


def reorder_top_level_decls(m: Module):
    imports: List[Decl] = [d for d in m.top_level_decls if isinstance(d, Import)]
    vars = [d for d in m.top_level_decls if isinstance(d, VarDecl)]
    funs = [d for d in m.top_level_decls if type(d) is FunDecl]
    m.top_level_decls = imports + vars + funs


class CheckConstants(AstWalker):
    compiler: CompilationCtx

    def __init__(self, compiler: CompilationCtx):
        self.compiler = compiler

    def walk_var_decl(self, n: 'VarDecl'):
        if not is_top_level(n):
            return
        if not isinstance(n.initializer, Literal):
            self.compiler.add_error_to_node(
                node=n.initializer,
                message="Global variable initializer can only be a literal",
                hint="Replace with a literal"
            )


class ResolverTransformer(AstTransformer):
    compiler: CompilationCtx
    builtins_scope: Scope
    scope_node: Scope

    def __init__(self, compiler: CompilationCtx):
        super().__init__()
        self.compiler = compiler
        self.builtins_scope = Scope()
        for d in builtin_declarations:
            self.builtins_scope.declare(d)

    @property
    def scope(self) -> Scope:
        assert self.scope_node is not None
        return self.scope_node

    def enter_scope(self, n: 'Scope'):
        self.scope_node = n

    def exit_scope(self, at_root=False):
        self.scope_node = outerscope(self.scope_node)
        if at_root:
            assert self.scope_node is None
        else:
            assert self.scope_node is not None

    def find_decl(self, name: str) -> Union[Decl, None]:
        cur = self.scope_node
        while cur is not None and name not in cur:
            cur = outerscope(cur)
        if cur is not None and name in cur:
            return cur.get_declaration(name)
        elif name in self.builtins_scope:
            return self.builtins_scope.get_declaration(name)
        else:
            return None

    def declare(self, d: Decl):
        if d.declared_name() in self.scope:
            other_d = self.scope.get_declaration(d.declared_name())
            self.compiler.add_error_to_node(
                d,
                f"Name '{d.declared_name()}' is already bound in the same scope",
                f"There is already a declaration with the same name at '{fancy_pos(other_d)}'"
            )
        else:
            self.scope.declare(d)

    def visit_declaration(self, n: 'Decl', d: None) -> 'Decl':
        if not is_top_level(n):
            self.declare(n)
        return super().visit_declaration(n, None)

    def visit_module(self, m: 'Module', d: None) -> 'Module':
        self.enter_scope(m)
        # in module declarations are unordered
        for i in m.imports:
            self.declare(i)
        for d in m.top_level_decls:
            self.declare(d)
        res = super().visit_module(m, None)
        self.exit_scope(at_root=True)
        return res

    def visit_fun_decl(self, fn: 'FunDecl', d: None):
        self.enter_scope(fn)
        res = super().visit_fun_decl(fn, None)
        self.exit_scope()
        return res

    def visit_stmt_block(self, n: 'StmtBlock', d):
        self.enter_scope(n)
        res = super().visit_stmt_block(n, None)
        self.exit_scope()
        return res

    def visit_ident_expr(self, i: 'IdentExpr', d: None):
        decl = self.find_decl(i.name)
        if decl is not None:
            return IdentExpr(
                name=i.name,
                span=i.span,
                decl=decl
            )
        else:
            self.compiler.add_error_to_node(i, f"Symbol '{i.name}' not found.")
            return i

    def visit_dot_expr(self, n: 'DotExpr', data: None) -> 'Expr':
        def check_module(rec: 'Expr'):
            if not isinstance(rec, IdentExpr) or rec.decl is None or not isinstance(rec.decl, Import):
                return None
            m = rec.decl.imported_module
            assert m is not None
            return m

        receiver = self.visit(n.receiver, None)
        assert isinstance(receiver, Expr)
        mod = check_module(receiver)
        if mod is None:
            self.compiler.add_error_to_node(
                node=receiver,
                message="Dot operations can only be used to reference module members"
            )
            return n
        member = mod.get_declaration(n.name) if n.name in mod else None
        if member is None:
            self.compiler.add_error_to_node(
                node=n,
                message=f"Cannot find declaration '{n.name}' in module {mod.name}"
            )
            return n
        # replace reference by ident
        return IdentExpr(
            name=f"{mod.name}@{n.name}",
            decl=member,
            span=n.span
        )
