from src.ast import FunCall, Module, AstTransformer, Node
from src.ast.builtins import Print
from src.context.compilation_ctx import CompilationCtx


def builtins(ctx: CompilationCtx, mod: Module):
    mod.accept(PrintTransformer(ctx), None)


class PrintTransformer(AstTransformer):
    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    def visit_fun_call(self, call: 'FunCall', data) -> Node:
        if call.name != "print":
            self.ctx.add_error_to_node(call, message="You can only call the 'print' builtin", hint="")
            return super().visit_fun_call(call, data)
        if len(call.args) != 1:
            self.ctx.add_error_to_node(call, message="The 'print' builtin accepts only 1 argument", hint="")
            return super().visit_fun_call(call, data)

        arg = call.args[0].accept(self, None)
        return Print(arg=arg, span=call.span)
