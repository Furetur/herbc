from src.ast import FunCall, Module, AstTransformer, Node
from src.ast.builtins import PrintInt, PrintBool, PrintStr
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyInt, TyBool, TyVoid, TyUnknown, TyStr


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
        assert arg.ty is not None and arg.ty is not TyUnknown
        if arg.ty is TyInt:
            return PrintInt(arg=arg, span=call.span)
        elif arg.ty is TyBool:
            return PrintBool(arg=arg, span=call.span)
        elif arg.ty is TyStr:
            return PrintStr(arg=arg, span=call.span)

