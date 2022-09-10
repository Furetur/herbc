from src.ast import AstVisitor, Module, FunDecl, IntLiteral, FunCall, BoolLiteral, Node, StrLiteral, VarDecl, \
    Print
from src.gen.defs import *
from src.ty import TyInt, TyBool, TyStr


class GenVisitor(AstVisitor):
    module: ir.Module
    builder: ir.IRBuilder
    print_int: ir.Function

    global_id: int = 0

    def __init__(self, m: Module):
        self.module = ir.Module(name=m.name)
        self.module.triple = "x86_64-pc-linux-gnu"
        self.print_int = ir.Function(self.module, print_int_fn_type, name=PRINT_INT_FN_NAME)
        self.print_bool = ir.Function(self.module, print_bool_fn_type, name=PRINT_BOOL_FN_NAME)
        self.print_str = ir.Function(self.module, print_str_fn_type, name=PRINT_STR_FN_NAME)

    def gen_string(self, value: str) -> ir.GlobalVariable:
        data = bytes(value, encoding='utf-8') + b'\0'
        typ = ir.ArrayType(ir.IntType(8), len(data))
        lit = ir.GlobalVariable(self.module, typ, name=f"strlit.{self.global_id}")
        lit.global_constant = True
        lit.initializer = ir.Constant(typ, bytearray(data))
        self.global_id += 1
        return lit

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

    def visit_print(self, n: 'Print', data):
        arg = n.arg.accept(self, None)
        if n.arg.ty == TyInt:
            fn = self.print_int
        elif n.arg.ty == TyBool:
            fn = self.print_bool
        elif n.arg.ty == TyStr:
            fn = self.print_str
        else:
            assert False, "unreachable"
        self.builder.call(fn, [arg])

    def visit_int_literal(self, lit: 'IntLiteral', data) -> ir.Constant:
        return ir.Constant(int_type, lit.value)

    def visit_bool_literal(self, lit: 'BoolLiteral', data) -> ir.Constant:
        return ir.Constant(bool_type, 1 if lit.value else 0)

    def visit_str_literal(self, n: 'StrLiteral', data) -> ir.Constant:
        if isinstance(n.parent, VarDecl):
            return None
        lit = self.gen_string(n.value)
        byteptr = self.builder.bitcast(lit, str_type)
        return byteptr
