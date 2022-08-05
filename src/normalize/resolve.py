from typing import Union

from src.ast import Module, AstVisitor, Scope, ScopeNode, Decl, FunDecl, IdentExpr, VarDecl, Import
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted


def resolve(compiler: CompilationCtx, mod: Module):
    v = ResolverVisitor(compiler)
    v.visit(mod)
    if compiler.has_errors():
        raise CompilationInterrupted()


class ResolverVisitor(AstVisitor):
    compiler: CompilationCtx
    scope_node: Union[ScopeNode, None] = None

    def __init__(self, compiler: CompilationCtx):
        self.compiler = compiler

    @property
    def scope(self) -> Scope:
        assert self.scope_node is not None
        return self.scope_node.scope

    def enter_scope(self, n: ScopeNode):
        self.scope_node = n

    def exit_scope(self, at_root=False):
        self.scope_node = self.scope_node.parent_scope()
        if at_root:
            assert self.scope_node is None
        else:
            assert self.scope_node is not None

    def find_decl(self, name: str) -> Union[Decl, None]:
        cur = self.scope_node
        while cur is not None and name not in cur.scope:
            cur = cur.parent_scope()
        if cur is not None and name in cur.scope:
            return cur.scope.get_declaration(name)
        else:
            return None

    def visit_decl(self, d: Decl):
        if d.is_top_level():
            # top level declarations are predeclared
            assert self.scope.get_declaration(d.declared_name()) is d
            return
        if d.declared_name() in self.scope:
            other_d = self.scope.get_declaration(d.declared_name())
            self.compiler.add_error_to_node(
                d,
                f"Name '{d.declared_name()}' is already bound in the same scope",
                f"There is already a declaration with the same name at '{other_d.human_readable_position()}'"
            )
        else:
            self.scope.declare(d)

    def visit_module(self, m: 'Module'):
        self.enter_scope(m)
        # in module declarations are unordered
        for i in m.imports:
            self.visit(i)
        for d in m.top_level_decls:
            m.scope.declare(d)
        for d in m.top_level_decls:
            self.visit(d)
        self.exit_scope(at_root=True)

    def visit_import(self, i: 'Import'):
        self.visit_decl(i)

    def visit_fun_decl(self, fn: 'FunDecl'):
        self.visit_decl(fn)
        self.enter_scope(fn)
        super().visit_fun_decl(fn)
        self.exit_scope()

    def visit_var_decl(self, v: 'VarDecl'):
        self.visit_decl(v)
        self.visit(v.initializer)

    def visit_ident_expr(self, i: 'IdentExpr'):
        decl = self.find_decl(i.name)
        if decl is not None:
            i.decl = decl
        else:
            self.compiler.add_error_to_node(i, f"Variable '{i.name}' not found.", "")
