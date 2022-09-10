from typing import Union

from src.ast import Module, AstWalker, Scope, Decl, FunDecl, IdentExpr, VarDecl, Import, FunCall, Node
from src.ast.utils import is_top_level, fancy_pos, outerscope
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.ty import TyBool, TyInt, TyVoid


def resolve(compiler: CompilationCtx, mod: Module):
    v = ResolverVisitor(compiler)
    mod.accept(v, None)
    if compiler.has_errors():
        raise CompilationInterrupted()


class ResolverVisitor(AstWalker):
    compiler: CompilationCtx
    scope_node: Scope

    def __init__(self, compiler: CompilationCtx):
        super().__init__()
        self.compiler = compiler

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
        else:
            return None

    def try_declare(self, d: Decl):
        if is_top_level(d):
            # top level declarations are predeclared
            assert self.scope.get_declaration(d.declared_name()) is d
        elif d.declared_name() in self.scope:
            other_d = self.scope.get_declaration(d.declared_name())
            self.compiler.add_error_to_node(
                d,
                f"Name '{d.declared_name()}' is already bound in the same scope",
                f"There is already a declaration with the same name at '{fancy_pos(other_d)}'"
            )
        else:
            self.scope.declare(d)

    def walk_declaration(self, n: 'Decl'):
        self.try_declare(n)
        super().walk_declaration(n)

    def walk_module(self, m: 'Module'):
        self.enter_scope(m)
        # in module declarations are unordered
        for i in m.imports:
            self.walk(i)
        for d in m.top_level_decls:
            m.declare(d)
        for d in m.top_level_decls:
            self.walk(d)
        self.exit_scope(at_root=True)

    def walk_fun_decl(self, fn: 'FunDecl'):
        self.try_declare(fn)
        self.enter_scope(fn)
        super().walk_declaration(fn)
        self.exit_scope()

    def walk_ident_expr(self, i: 'IdentExpr'):
        decl = self.find_decl(i.name)
        if decl is not None:
            i.decl = decl
        else:
            self.compiler.add_error_to_node(i, f"Variable '{i.name}' not found.", "")
