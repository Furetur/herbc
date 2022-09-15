from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.ast import *


D = TypeVar("D")
R = TypeVar("R")


class AstVisitor(Generic[D, R], ABC):

    def visit(self, n: 'Node', data: D) -> R:
        return n.accept(self, data)

    @abstractmethod
    def visit_node(self, n: 'Node', data: D) -> R: ...

    def visit_module(self, n: 'Module', data: D) -> R:
        return self.visit_node(n, data)

    # declarations

    def visit_declaration(self, n: 'Decl', data: D) -> R:
        return self.visit_statement(n, data)

    def visit_import(self, n: 'Import', data: D) -> R:
        return self.visit_declaration(n, data)

    def visit_fun_decl(self, n: 'FunDecl', data: D) -> R:
        return self.visit_declaration(n, data)

    def visit_var_decl(self, n: 'VarDecl', data: D) -> R:
        return self.visit_declaration(n, data)

    # expressions

    def visit_expression(self, n: 'Expr', data: D) -> R:
        return self.visit_node(n, data)

    def visit_binop(self, n: 'BinopExpr', data: D) -> R:
        return self.visit_expression(n, data)

    def visit_int_literal(self, n: 'IntLiteral', data: D) -> R:
        return self.visit_expression(n, data)

    def visit_bool_literal(self, n: 'BoolLiteral', data: D) -> R:
        return self.visit_expression(n, data)

    def visit_str_literal(self, n: 'StrLiteral', data: D) -> R:
        return self.visit_expression(n, data)

    def visit_fun_call(self, n: 'FunCall', data: D) -> R:
        return self.visit_expression(n, data)

    def visit_ident_expr(self, n: 'IdentExpr', data: D) -> R:
        return self.visit_expression(n, data)


    def visit_print(self, n: 'Print', data: D) -> R:
        return self.visit_expression(n, data)

    # statements

    def visit_stmt_block(self, n: 'StmtBlock', data: D) -> R:
        return self.visit_statement(n, data)

    def visit_expr_stmt(self, n: 'ExprStmt', data: D) -> R:
        return self.visit_statement(n, data)

    def visit_assign_stmt(self, n: 'AssignStmt', data: D) -> R:
        return self.visit_statement(n, data)

    def visit_if_stmt(self, n: 'IfStmt', data: D) -> R:
        return self.visit_statement(n, data)

    def visit_statement(self, n: 'Stmt', data: D) -> R:
        return self.visit_node(n, data)
