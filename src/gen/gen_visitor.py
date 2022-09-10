import dataclasses
from typing import Dict

from src.ast import AstVisitor, Module, FunDecl, IntLiteral, FunCall, BoolLiteral, Node, StrLiteral, VarDecl, \
    Print, IdentExpr
from src.ast.utils import is_top_level
from src.context.compilation_ctx import CompilationCtx
from src.gen.defs import *
from src.ty import TyInt, TyBool, TyStr


class GenVisitor(AstVisitor):
    ctx: CompilationCtx
    module_node: Module

    # generation
    module: ir.Module
    builder: ir.IRBuilder | None

    header: Dict[str, ir.GlobalValue]

    global_id: int = 0
    globals: Dict[str, ir.GlobalVariable]

    locals: Dict[Decl, ir.Value] # map[local var decl, stack alloca]

    def __init__(self, ctx: CompilationCtx, mod: Module):
        self.ctx = ctx
        self.module_node = mod
        self.module = ir.Module(name=mod.unique_name)
        self.header = dict()
        self.globals = dict()
        self.locals = dict()

    def generate(self) -> ir.Module:
        self.init_module()
        self.visit_module(self.module_node, None)
        return self.module

    def init_module(self):
        self.module.triple = LL_TRIPLE
        self.header[PRINT_INT_FN_NAME] = ir.Function(self.module, print_int_fn_type, name=PRINT_INT_FN_NAME)
        self.header[PRINT_BOOL_FN_NAME] = ir.Function(self.module, print_bool_fn_type, name=PRINT_BOOL_FN_NAME)
        self.header[PRINT_STR_FN_NAME] = ir.Function(self.module, print_str_fn_type, name=PRINT_STR_FN_NAME)

    def next_global_id(self) -> int:
        id = self.global_id
        self.global_id += 1
        return id

    # Reusable functions

    def gen_str_literal(self, value: str) -> ir.GlobalVariable:
        data = bytes(value, encoding='utf-8') + b'\0'
        lit_name = f"{self.module_node.unique_name}.strlit.{self.next_global_id()}"

        typ = ir.ArrayType(byte_type, len(data))
        lit = ir.GlobalVariable(self.module, typ, name=lit_name)
        lit.global_constant = True
        lit.initializer = ir.Constant(typ, bytearray(data))
        self.globals[lit_name] = lit
        return lit

    # Visitor

    def visit_node(self, n: Node, data):
        n.accept_children(self, data)

    def visit_fun_decl(self, fn: 'FunDecl', data):
        assert fn.name == "main"
        f = ir.Function(self.module, main_fn_type, name=MAIN_FN_NAME)
        self.builder = ir.IRBuilder(f.append_basic_block(name="entry"))

        for stmt in fn.body:
            stmt.accept(self, None)

        self.builder.ret(ir.Constant(int_type, 0))

    def visit_var_decl(self, n: 'VarDecl', data):
        if is_top_level(n):
            # global variable
            name = global_name(n)
            glob = ir.GlobalVariable(self.module, ll_type(n.ty), name=name)
            glob.initializer = n.initializer.accept(self, None)
            self.globals[name] = glob
        else:
            # local variable
            alloca = self.builder.alloca(ll_type(n.ty))
            initializer = n.initializer.accept(self, None)
            self.builder.store(initializer, alloca)
            self.locals[n] = alloca

    def visit_fun_call(self, call: 'FunCall', data):
        assert False

    def visit_print(self, n: 'Print', data):
        arg = n.arg.accept(self, None)
        if n.arg.ty == TyInt:
            fn = self.header[PRINT_INT_FN_NAME]
        elif n.arg.ty == TyBool:
            fn = self.header[PRINT_BOOL_FN_NAME]
        elif n.arg.ty == TyStr:
            fn = self.header[PRINT_STR_FN_NAME]
        else:
            assert False, "unreachable"
        self.builder.call(fn, [arg])

    def visit_ident_expr(self, n: 'IdentExpr', data) -> ir.Value:
        assert n.decl is not None
        if is_top_level(n.decl):
            # global variable
            ptr = self.globals[global_name(n.decl)]
            assert ptr is not None, "Global variable was not generated"
        else:
            # local variable
            ptr = self.locals[n.decl]
            assert ptr is not None, "Local is not generated"
        load = self.builder.load(ptr)
        return self.builder.bitcast(load, ll_type(n.ty))

    def visit_int_literal(self, lit: 'IntLiteral', data) -> ir.Constant:
        return ir.Constant(int_type, lit.value)

    def visit_bool_literal(self, lit: 'BoolLiteral', data) -> ir.Constant:
        return ir.Constant(bool_type, 1 if lit.value else 0)

    def visit_str_literal(self, n: 'StrLiteral', data) -> ir.Value:
        return self.gen_str_literal(n.value).bitcast(str_type)

