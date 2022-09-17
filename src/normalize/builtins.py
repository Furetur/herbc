from src.ast import FunCall, Module, AstTransformer, Node, IdentExpr, Expr
from src.ast.builtins import Print, PrintBuiltinDecl
from src.context.compilation_ctx import CompilationCtx


def builtins(ctx: CompilationCtx, mod: Module):
    mod.accept(PrintTransformer(ctx), None)


class PrintTransformer(AstTransformer):
    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    def visit_fun_call(self, call: 'FunCall', data) -> Node:
        callee = call.callee
        if not isinstance(callee, IdentExpr):
            return super().visit_fun_call(call, data)
        assert callee.decl is not None
        if callee.decl != PrintBuiltinDecl:
            return super().visit_fun_call(call, data)
        # it is a 'print' call
        if len(call.args) != 1:
            self.ctx.add_error_to_node(call, message="The 'print' builtin accepts only 1 argument", hint="")
            return super().visit_fun_call(call, data)

        arg: 'Expr' = self.visit(call.args[0], None)
        return Print(arg=arg, span=call.span)
