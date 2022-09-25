from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ast import *
from src.ast.visitors.ast_visitor import AstVisitor


class AstWalker(AstVisitor[None, None]):
    def walk(self, n: 'Node'):
        n.accept(self, None)

    def walk_node(self, n: 'Node'):
        n.accept_children(self, None)

    def visit_node(self, n: 'Node', data: None):
        self.walk_node(n)

    def walk_module(self, n: 'Module'):
        self.walk_node(n)

    def visit_module(self, n: 'Module', data: None):
        self.walk_module(n)

    # declarations

    def walk_declaration(self, n: 'Decl'):
        self.walk_statement(n)

    def visit_declaration(self, n: 'Decl', data: None):
        self.walk_declaration(n)

    def walk_import(self, n: 'Import'):
        self.walk_declaration(n)

    def visit_import(self, n: 'Import', data: None):
        self.walk_import(n)

    def walk_entry(self, n: 'Entrypoint'):
        self.walk_declaration(n)

    def visit_entry(self, n: 'Entrypoint', data: None):
        self.walk_entry(n)

    def walk_fun_decl(self, n: 'FunDecl'):
        self.walk_declaration(n)

    def visit_fun_decl(self, n: 'FunDecl', data: None):
        self.walk_fun_decl(n)

    def walk_var_decl(self, n: 'VarDecl'):
        self.walk_declaration(n)

    def visit_var_decl(self, n: 'VarDecl', data: None):
        self.walk_var_decl(n)

    def walk_arg_decl(self, n: 'ArgDecl'):
        self.walk_declaration(n)

    def visit_arg_decl(self, n: 'ArgDecl', data: None):
        self.walk_arg_decl(n)

    # expressions

    def walk_expression(self, n: 'Expr'):
        self.walk_node(n)

    def visit_expression(self, n: 'Expr', data: None):
        self.walk_expression(n)

    def walk_binop(self, n: 'BinopExpr'):
        self.walk_expression(n)

    def visit_binop(self, n: 'BinopExpr', data: 'D'):
        self.walk_binop(n)

    def walk_unop(self, n: 'UnopExpr'):
        self.walk_expression(n)

    def visit_unop(self, n: 'UnopExpr', data: 'D'):
        self.walk_unop(n)

    def walk_int_literal(self, n: 'IntLiteral'):
        self.walk_expression(n)

    def visit_int_literal(self, n: 'IntLiteral', data: None):
        self.walk_int_literal(n)

    def walk_bool_literal(self, n: 'BoolLiteral'):
        self.walk_expression(n)

    def visit_bool_literal(self, n: 'BoolLiteral', data: None):
        self.walk_bool_literal(n)

    def walk_str_literal(self, n: 'StrLiteral'):
        self.walk_expression(n)

    def visit_str_literal(self, n: 'StrLiteral', data: None):
        self.walk_str_literal(n)

    def walk_fun_call(self, n: 'FunCall'):
        self.walk_expression(n)

    def visit_fun_call(self, n: 'FunCall', data: None):
        self.walk_fun_call(n)

    def walk_print(self, n: 'Print'):
        self.walk_expression(n)

    def visit_print(self, n: 'Print', data: None):
        self.walk_print(n)

    def walk_ident_expr(self, n: 'IdentExpr'):
        self.walk_expression(n)

    def visit_ident_expr(self, n: 'IdentExpr', data: None):
        self.walk_ident_expr(n)

    # statements

    def walk_statement(self, n: 'Stmt'):
        self.walk_node(n)

    def visit_statement(self, n: 'Stmt', data: None):
        self.walk_statement(n)

    def walk_stmt_block(self, n: 'StmtBlock'):
        self.walk_node(n)

    def visit_stmt_block(self, n: 'StmtBlock', data: 'D'):
        self.walk_stmt_block(n)

    def walk_expr_stmt(self, n: 'ExprStmt'):
        self.walk_statement(n)

    def visit_expr_stmt(self, n: 'ExprStmt', data: None):
        self.walk_expr_stmt(n)

    def walk_assign_stmt(self, n: 'AssignStmt'):
        self.walk_statement(n)

    def visit_assign_stmt(self, n: 'AssignStmt', data: None):
        self.walk_assign_stmt(n)

    def walk_if_stmt(self, n: 'IfStmt'):
        self.walk_statement(n)

    def visit_if_stmt(self, n: 'IfStmt', data: None):
        self.walk_if_stmt(n)

    def walk_while_stmt(self, n: 'WhileStmt'):
        self.walk_statement(n)

    def visit_while_stmt(self, n: 'WhileStmt', data: None):
        self.walk_while_stmt(n)

    def walk_ret(self, n: 'RetStmt'):
        self.walk_statement(n)

    def visit_ret(self, n: 'RetStmt', data: None):
        self.walk_ret(n)
