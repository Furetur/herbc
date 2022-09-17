import dataclasses
from typing import Dict

from src.ast import AstVisitor, Module, FunDecl, IntLiteral, FunCall, BoolLiteral, Node, StrLiteral, VarDecl, \
    Print, IdentExpr, AssignStmt, BinopKind, IfStmt, WhileStmt, BinopExpr, UnopExpr, UnopKind
from src.ast.utils import is_top_level, find_descendants_of_type
from src.context.compilation_ctx import CompilationCtx
from src.gen.defs import *
from src.ty import TyInt, TyBool, TyStr


class GenVisitor(AstVisitor):
    ctx: CompilationCtx
    module_node: Module

    # generation
    module: ir.Module
    f: ir.Function | None
    builder: ir.IRBuilder | None

    header: Dict[str, ir.GlobalValue]

    global_id: int = 0
    globals: Dict[str, ir.GlobalVariable]

    locals: Dict[Decl, ir.AllocaInstr] # map[local var decl, stack alloca]

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

    def gen_ptr_to_decl(self, decl: Decl) -> ir.Value:
        if is_top_level(decl):
            # global variable
            name = global_name(decl)
            assert name in self.globals, "Global variable was not generated"
            return self.globals[global_name(decl)]
        else:
            # local variable
            assert decl in self.locals, "Local variable was not generated"
            return self.locals[decl]

    def stack_alloc_if_needed(self, n: 'VarDecl') -> ir.AllocaInstr:
        if n in self.locals:
            return self.locals[n]
        alloca = self.builder.alloca(ll_type(n.ty))
        self.locals[n] = alloca
        return alloca

    # Visitor

    def visit_node(self, n: Node, data):
        n.accept_children(self, data)

    # Declarations

    def visit_fun_decl(self, fn: 'FunDecl', data):
        if fn.name != USER_MAIN_FN_NAME:
            return
        f = ir.Function(self.module, main_fn_type, name=OUT_MAIN_FN_NAME)
        self.f = f
        self.builder = ir.IRBuilder(f.append_basic_block(name="entry"))
        fn.body.accept(self, None)
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
            alloca = self.stack_alloc_if_needed(n)
            initializer = n.initializer.accept(self, None)
            self.builder.store(initializer, alloca)

    # Statements

    def visit_assign_stmt(self, n: 'AssignStmt', data):
        assert isinstance(n.lvalue, IdentExpr) and n.lvalue.decl is not None
        ptr = self.gen_ptr_to_decl(n.lvalue.decl)
        value = n.rvalue.accept(self, None)
        self.builder.store(value, ptr)

    def visit_if_stmt(self, n: 'IfStmt', data):
        # the basic block after the if statement
        after = self.builder.append_basic_block()

        for cond, block in n.condition_branches:
            then = self.builder.append_basic_block()
            els = self.builder.append_basic_block()
            # finish the current basic block
            self.builder.cbranch(self.visit(cond, None), then, els)
            # generate 'then'
            self.builder = ir.IRBuilder(then)
            self.visit(block, None)
            self.builder.branch(after) # IMPORTANT: jump to 'after'
            # switch to generating 'else'
            # the next if condition should be generated inside this else basic block
            self.builder = ir.IRBuilder(els)
        # generate 'else' branch
        # self.builder already points to the final else branch
        # if there's no else branch we generate empty else block that jumps to 'before'
        if n.else_branch is not None:
            self.visit(n.else_branch, None)
        self.builder.branch(after) # IMPORTANT: jump to 'after'
        self.builder = ir.IRBuilder(after)

    def visit_while_stmt(self, n: 'WhileStmt', data):
        for var in find_descendants_of_type(n, VarDecl):
            self.stack_alloc_if_needed(var)
        # generate while
        cond_block = self.builder.append_basic_block()
        body_block = self.builder.append_basic_block()
        after_block = self.builder.append_basic_block()

        self.builder.branch(cond_block) # finish current block
        # condition block
        self.builder = ir.IRBuilder(cond_block)
        cond: ir.Value = self.visit(n.cond, None)
        self.builder.cbranch(cond, body_block, after_block)
        # body block
        self.builder = ir.IRBuilder(body_block)
        self.visit(n.body, None)
        self.builder.branch(cond_block)
        # after block
        self.builder = ir.IRBuilder(after_block)

    # Expressions

    def visit_binop(self, n: 'BinopExpr', data) -> ir.Value:
        left = n.left.accept(self, None)
        right = n.right.accept(self, None)
        if n.kind == BinopKind.PLUS:
            return self.builder.add(left, right)
        elif n.kind == BinopKind.MUL:
            return self.builder.mul(left, right)
        elif n.kind == BinopKind.DIV:
            return self.builder.sdiv(left, right)
        elif n.kind == BinopKind.MINUS:
            return self.builder.sub(left, right)
        elif n.kind in [BinopKind.BITWISE_AND, BinopKind.LOGICAL_AND]:
            return self.builder.and_(left, right)
        elif n.kind in [BinopKind.BITWISE_OR, BinopKind.LOGICAL_OR]:
            return self.builder.or_(left, right)
        elif n.kind in [BinopKind.LT, BinopKind.LTE, BinopKind.EQ, BinopKind.NEQ, BinopKind.GT, BinopKind.GTE]:
            return self.builder.icmp_signed(n.kind.value, left, right)
        elif n.kind == BinopKind.MOD:
            return self.builder.srem(left, right)
        else:
            assert False

    def visit_unop(self, n: 'UnopExpr', data) -> ir.Value:
        expr = n.expr.accept(self, None)
        if n.kind == UnopKind.MINUS:
            return self.builder.neg(expr)
        elif n.kind == UnopKind.BANG:
            return self.builder.not_(expr)
        else:
            assert False

    def visit_fun_call(self, call: 'FunCall', data):
        assert False

    def visit_print(self, n: 'Print', data):
        arg: ir.Value = n.arg.accept(self, None)
        if n.arg.ty == TyInt:
            fn = self.header[PRINT_INT_FN_NAME]
        elif n.arg.ty == TyBool:
            fn = self.header[PRINT_BOOL_FN_NAME]
            arg = self.builder.zext(arg, byte_type)
        elif n.arg.ty == TyStr:
            fn = self.header[PRINT_STR_FN_NAME]
        else:
            assert False, "unreachable"
        self.builder.call(fn, [arg])

    def visit_ident_expr(self, n: 'IdentExpr', data) -> ir.Value:
        assert n.decl is not None
        ptr = self.gen_ptr_to_decl(n.decl)
        load = self.builder.load(ptr)
        return self.builder.bitcast(load, ll_type(n.ty))

    def visit_int_literal(self, lit: 'IntLiteral', data) -> ir.Constant:
        return ir.Constant(int_type, lit.value)

    def visit_bool_literal(self, lit: 'BoolLiteral', data) -> ir.Constant:
        return ir.Constant(bool_type, 1 if lit.value else 0)

    def visit_str_literal(self, n: 'StrLiteral', data) -> ir.Value:
        return self.gen_str_literal(n.value).bitcast(str_type)

