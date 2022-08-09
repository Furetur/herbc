from src.ast import FunCall, Module, AstTransformer, Node
from src.ast.builtins import PrintInt, PrintBool
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyInt, TyBool, TyVoid


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
        assert arg.ty is TyInt or arg.ty is TyBool
        if arg.ty is TyInt:
            new = PrintInt(arg=arg, span=call.span, ty=TyVoid, parent=None)
            arg.parent = new
            new.parent = call.parent
            return new
        else:
            new = PrintBool(arg=arg, span=call.span, ty=TyVoid, parent=None)
            arg.parent = new
            new.parent = call.parent
            return new
