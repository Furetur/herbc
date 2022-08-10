from src.ast import Module
from src.ast.fixverify import set_parents
from src.context.compilation_ctx import CompilationCtx
from src.normalize.builtins import builtins
from src.normalize.check_main import check_main
from src.normalize.evaluate import evaluate
from src.normalize.reorder import reorder_top_level_decls
from src.normalize.resolve import resolve
from src.normalize.typecheck import typecheck


def normalize(ctx: CompilationCtx, module: Module):
    resolve(ctx, module)
    check_main(ctx, module)
    reorder_top_level_decls(ctx, module)
    typecheck(ctx, module)
    builtins(ctx, module)
    set_parents(module)
    evaluate(ctx, module)
    set_parents(module)
