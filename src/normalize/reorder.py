import graphlib
from collections import defaultdict
from typing import Set, List, cast, Dict, Iterable

from src.ast import Module, Decl, IdentExpr, VarDecl, FunDecl, Node, AstWalker
from src.ast.utils import module, is_top_level
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted


def reorder_top_level_decls(ctx: CompilationCtx, m: Module):
    """
    Reorders top level declarations on the module: first come VarDecls, then FunDecls.
    Additionally, all VarDecls are topologically sorted
    """
    funs = [d for d in m.top_level_decls if type(d) is FunDecl]
    m.top_level_decls = get_var_decl_order(ctx, m) + funs


def get_var_decl_order(ctx: CompilationCtx, m: Module) -> List[VarDecl]:
    vars: Dict[str, VarDecl] = {d.declared_name(): cast(VarDecl, d) for d in m.top_level_decls if type(d) is VarDecl}
    # build graph
    finder = ReferenceFinder()
    graph = dict()
    for v in vars.values():
        refs = finder.find_refs(v.initializer)
        graph[v.declared_name()] = set()
        for r in refs:
            if type(r) is VarDecl and is_top_level(r) and module(r) is m:
                graph[v.declared_name()].add(r.declared_name())
    # topological sort
    try:
        order = list(graphlib.TopologicalSorter(graph).static_order())
    except graphlib.CycleError as e:
        cycle = e.args[1]
        assert len(cycle) > 0
        decl = m.get_declaration(cycle[0])
        ctx.add_error_to_node(decl, message="Declarations are cyclic", hint=" -> ".join(cycle))
        raise CompilationInterrupted()
    return [vars[name] for name in order]


class ReferenceFinder(AstWalker):
    # TODO: Decl is not hashable
    references: List[Decl]

    def __init__(self):
        self.references = list()

    def find_refs(self, n: Node) -> Iterable[Decl]:
        self.clear()
        self.walk(n)
        return self.references

    def clear(self):
        self.references.clear()

    def walk_ident_expr(self, i: 'IdentExpr'):
        assert i.decl is not None
        if i.decl not in self.references:
            self.references.append(i.decl)
