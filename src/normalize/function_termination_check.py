from src.ast import AstVisitor, Node, IfStmt, StmtBlock, FunDecl, WhileStmt, RetStmt, Module
from src.context.compilation_ctx import CompilationCtx
from src.ty import TyVoid


class FunctionTerminationChecker(AstVisitor[None, bool]):
    def __init__(self, ctx: 'CompilationCtx'):
        self.ctx = ctx

    def visit_node(self, n: 'Node', data: None) -> bool:
        return False

    def visit_module(self, n: 'Module', data: None):
        for decl in n.top_level_decls:
            self.visit(decl, None)

    def visit_fun_decl(self, n: 'FunDecl', data: None) -> bool:
        returns = self.visit(n.body, None)
        if n.ret_ty != TyVoid and not returns:
            self.ctx.add_error_to_node(
                node=n,
                message=f"The '{n.name}' must return a value in all cases",
                hint="You might have forgotten a return statement"
            )
        return returns

    def visit_if_stmt(self, n: 'IfStmt', data: None) -> bool:
        result = True
        for _, block in n.condition_branches:
            result &= self.visit(block, None)
        if n.else_branch is not None:
            result &= self.visit(n.else_branch, None)
        else:
            result = False
        return result

    def visit_stmt_block(self, n: 'StmtBlock', data: None) -> bool:
        result = False
        for stmt in n.stmts:
            if not result:
                result |= self.visit(stmt, None)
            else:
                # already terminated
                self.ctx.add_error_to_node(
                    node=stmt,
                    message="This statement is unreachable",
                    hint="You have a return statement somewhere above"
                )
                return result
        return result

    def visit_ret(self, n: 'RetStmt', data: None) -> bool:
        return True
