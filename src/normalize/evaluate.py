from typing import cast, Dict
from copy import copy

from src.ast import Module, IntLiteral, Node, VarDecl, IdentExpr, Decl, BoolLiteral, Literal, \
    AstTransformer, AstWalker
from src.ast.utils import fancy_pos
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted


def evaluate(ctx: CompilationCtx, m: Module):
    c = CheckConstants(ctx)
    c.walk(m)
    if ctx.has_errors():
        raise CompilationInterrupted()
    v = EvaluateTransformer()
    m.accept(v, None)
    if ctx.has_errors():
        raise CompilationInterrupted()


class CheckConstants(AstWalker):
    """
    Check "const a = expr;" declarations
    """
    def __init__(self, ctx: CompilationCtx):
        super().__init__()
        self.ctx = ctx

    def walk_var_decl(self, v: 'VarDecl'):
        if not isinstance(v.initializer, Literal) and type(v.initializer) is not IdentExpr:
            self.ctx.add_error_to_node(
                v,
                message="Only literals and identifiers are allowed in const declarations",
                hint=f"expression at '{fancy_pos(v.initializer)}' is not a literal or an identifier"
            )


class EvaluateTransformer(AstTransformer):
    evaluated: Dict[Decl, Node]

    def __init__(self):
        self.evaluated = dict()

    def visit_ident_expr(self, i: 'IdentExpr', data: None) -> Literal:
        decl = cast(VarDecl, i.decl)
        assert decl is not None and type(decl) is VarDecl
        initializer = decl.initializer
        assert isinstance(initializer, Literal)
        return copy(initializer)
