
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ast.nodes import *
    from src.ast.expr_literals import *
    from src.ast.builtins import *


class AstVisitor:
    def visit(self, n: 'Node'):
        return n.accept(self)

    def visit_module(self, m: 'Module'):
        for i in m.imports:
            self.visit(i)
        for d in m.top_level_decls:
            self.visit(d)

    # declarations

    def visit_import(self, i: 'Import'):
        pass

    def visit_fun_decl(self, fn: 'FunDecl'):
        for stmt in fn.body:
            self.visit(stmt)

    def visit_var_decl(self, v: 'VarDecl'):
        return self.visit(v.initializer)

    # expressions

    def visit_int_literal(self, lit: 'IntLiteral'):
        pass

    def visit_bool_literal(self, lit: 'BoolLiteral'):
        pass

    def visit_fun_call(self, call: 'FunCall'):
        for expr in call.args:
            self.visit(expr)

    def visit_print_int(self, p: 'PrintInt'):
        self.visit(p.arg)

    def visit_print_bool(self, p: 'PrintBool'):
        self.visit(p.arg)

    # statements

    def visit_expr_stmt(self, stmt: 'ExprStmt'):
        return self.visit(stmt.expr)

    def visit_ident_expr(self, i: 'IdentExpr'):
        pass