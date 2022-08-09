from llvmlite import ir

from src.ast import AstVisitor, Module, FunDecl, IntLiteral, FunCall, BoolLiteral, Node
from src.ast.builtins import PrintBool, PrintInt
from src.gen.defs import main_fn_type, MAIN_FN_NAME, int_type, print_int_fn_type, PRINT_INT_FN_NAME, print_bool_fn_type, \
    PRINT_BOOL_FN_NAME, bool_type


class GenVisitor(AstVisitor):
    module: ir.Module
    builder: ir.IRBuilder
    print_int: ir.Function

    def __init__(self, m: Module):
        self.module = ir.Module(name=m.name)
        self.module.triple = "x86_64-pc-linux-gnu"
        self.print_int = ir.Function(self.module, print_int_fn_type, name=PRINT_INT_FN_NAME)
        self.print_bool = ir.Function(self.module, print_bool_fn_type, name=PRINT_BOOL_FN_NAME)

    def visit_node(self, n: Node, data):
        n.accept_children(self, data)

    def visit_fun_decl(self, fn: 'FunDecl', data):
        assert fn.name == "main"
        f = ir.Function(self.module, main_fn_type, name=MAIN_FN_NAME)
        self.builder = ir.IRBuilder(f.append_basic_block(name="entry"))

        for stmt in fn.body:
            stmt.accept(self, None)

        self.builder.ret(ir.Constant(int_type, 0))

    def visit_fun_call(self, call: 'FunCall', data):
        assert False

    def visit_print_int(self, p: 'PrintInt', data):
        arg = p.arg.accept(self, None)
        self.builder.call(self.print_int, [arg])

    def visit_print_bool(self, p: 'PrintBool', data):
        arg = p.arg.accept(self, None)
        self.builder.call(self.print_bool, [arg])

    def visit_int_literal(self, lit: 'IntLiteral', data) -> ir.Constant:
        return ir.Constant(int_type, lit.value)

    def visit_bool_literal(self, lit: 'BoolLiteral', data) -> ir.Constant:
        return ir.Constant(bool_type, 1 if lit.value else 0)
