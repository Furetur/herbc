from src.ast import AstVisitor, FunCall, Module
from src.ast.builtins import PrintInt, PrintBool
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyInt, TyBool, TyVoid


def builtins(ctx: CompilationCtx, mod: Module):
    PrintVisitor(ctx).visit(mod)


class PrintVisitor(AstVisitor):
    def __init__(self, ctx: CompilationCtx):
        self.ctx = ctx

    def visit_fun_call(self, call: 'FunCall'):
        if call.fn_name != "print":
            self.ctx.add_error_to_node(call, message="You can only call the 'print' builtin", hint="")
        else:
            if len(call.args) != 1:
                self.ctx.add_error_to_node(call, message="The 'print' builtin accepts only 1 argument", hint="")
            else:
                arg = call.args[0]
                assert arg.ty is TyInt or arg.ty is TyBool
                if arg.ty is TyInt:
                    new = PrintInt(arg=arg, span=call.span, ty=TyVoid, parent=None)
                    arg.parent = new
                    call.replace(new)
                else:
                    new = PrintBool(arg=arg, span=call.span, ty=TyVoid, parent=None)
                    arg.parent = new
                    call.replace(new)
        for arg in call.args:
            self.visit(arg)
