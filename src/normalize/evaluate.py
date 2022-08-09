from typing import cast, Dict

from src.ast import Module, AstVisitor, IntLiteral, Node, VarDecl, IdentExpr, Decl, BoolLiteral, Literal, AstTransformer
from src.ast.utils import fancy_pos
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.ty import TyInt, TyBool


def evaluate(ctx: CompilationCtx, m: Module):
    c = CheckConstants(ctx)
    m.accept(c, None)
    if ctx.has_errors():
        raise CompilationInterrupted()
    v = EvaluateTransformer()
    m.accept(v, None)
    if ctx.has_errors():
        raise CompilationInterrupted()


class CheckConstants(AstVisitor):
    """
    Check "const a = expr;" declarations
    """
    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    def visit_node(self, n: Node, data):
        n.accept_children(self, data)

    def visit_var_decl(self, v: 'VarDecl', data):
        if type(v.initializer) is not IntLiteral and type(v.initializer) is not BoolLiteral and type(v.initializer) is not IdentExpr:
            self.ctx.add_error_to_node(
                v,
                message="Only literals and identifiers are allowed in const declarations",
                hint=f"expression at '{fancy_pos(v.initializer)}' is not a literal or an identifier"
            )


class EvaluateTransformer(AstTransformer):
    evaluated: Dict[Decl, Node]

    def __init__(self):
        self.evaluated = dict()

    def visit_ident_expr(self, i: 'IdentExpr', data) -> Literal:
        decl = cast(VarDecl, i.decl)
        assert decl is not None and type(decl) is VarDecl
        initializer = decl.initializer
        assert isinstance(initializer, Literal)
        if isinstance(initializer, IntLiteral):
            return IntLiteral(value=initializer.value, span=i.span, parent=None)
        elif isinstance(initializer, BoolLiteral):
            return BoolLiteral(value=initializer.value, span=i.span, parent=None)
