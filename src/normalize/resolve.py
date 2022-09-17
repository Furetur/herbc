from typing import Union, List

from src.ast import Module, AstWalker, Scope, Decl, FunDecl, IdentExpr, VarDecl, Import, FunCall, Node, Literal, \
    StmtBlock, builtin_declarations
from src.ast.utils import is_top_level, fancy_pos, outerscope
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted


def resolve(compiler: CompilationCtx, mod: Module):
    reorder_top_level_decls(mod)
    mod.accept(CheckConstants(compiler), None)
    if compiler.has_errors():
        raise CompilationInterrupted()
    v = ResolverVisitor(compiler)
    mod.accept(v, None)
    if compiler.has_errors():
        raise CompilationInterrupted()


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

class ResolverVisitor(AstWalker):
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

    def walk_declaration(self, n: 'Decl'):
        if not is_top_level(n):
            self.declare(n)
        super().walk_declaration(n)

    def walk_module(self, m: 'Module'):
        self.enter_scope(m)
        # in module declarations are unordered
        for i in m.imports:
            self.walk(i)
        for d in m.top_level_decls:
            self.declare(d)
        for d in m.top_level_decls:
            self.walk(d)
        self.exit_scope(at_root=True)

    def walk_fun_decl(self, fn: 'FunDecl'):
        self.enter_scope(fn)
        super().walk_fun_decl(fn) # we cannot use walk_declaration because it will call the method above
        self.exit_scope()

    def walk_stmt_block(self, n: 'StmtBlock'):
        self.enter_scope(n)
        super().walk_node(n)
        self.exit_scope()

    def walk_ident_expr(self, i: 'IdentExpr'):
        decl = self.find_decl(i.name)
        if decl is not None:
            i.decl = decl
        else:
            self.compiler.add_error_to_node(i, f"Variable '{i.name}' not found.", "")
