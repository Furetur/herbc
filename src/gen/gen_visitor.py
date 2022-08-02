from llvmlite import ir

from src.ast import AstVisitor, Module, FunDecl, IntLiteral, FunCall
from src.gen.defs import main_fn_type, MAIN_FN_NAME, int_type, print_int_fn_type, PRINT_INT_FN_NAME


class GenVisitor(AstVisitor):
    module: ir.Module
    builder: ir.IRBuilder
    print_int: ir.Function

    def __init__(self, m: Module):
        self.module = ir.Module(name=m.name())
        self.module.triple = "x86_64-pc-linux-gnu"
        self.print_int = ir.Function(self.module, print_int_fn_type, name=PRINT_INT_FN_NAME)

    def visit_fun_decl(self, fn: 'FunDecl'):
        assert fn.name == "main"
        f = ir.Function(self.module, main_fn_type, name=MAIN_FN_NAME)
        self.builder = ir.IRBuilder(f.append_basic_block(name="entry"))

        for stmt in fn.body:
            self.visit(stmt)

        self.builder.ret(ir.Constant(int_type, 0))

    def visit_fun_call(self, call: 'FunCall'):
        assert call.fn_name == "print"
        assert len(call.args) == 1
        arg = self.visit(call.args[0])
        self.builder.call(self.print_int, [arg])

    def visit_int_literal(self, lit: 'IntLiteral') -> ir.Constant:
        return ir.Constant(int_type, lit.value)
