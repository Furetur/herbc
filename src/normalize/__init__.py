from src.ast import Module
from src.ast.fixverify import set_parents
from src.context.compilation_ctx import CompilationCtx
from src.normalize.builtins import builtins
from src.normalize.check_main import check_main
from src.normalize.resolve import resolve
from src.normalize.typecheck import typecheck


def normalize(ctx: CompilationCtx, module: Module):
    resolve(ctx, module)
    check_main(ctx, module)
    set_parents(module)
    typecheck(ctx, module)
    builtins(ctx, module)
    set_parents(module)
