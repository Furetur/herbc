from src.ast import Module
from src.ast.fixverify import set_parents
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.normalize.builtins import builtins
from src.normalize.check_main import check_main
from src.normalize.resolve import resolve
from src.normalize.typecheck import typecheck


def normalize(ctx: CompilationCtx, module: Module, is_entry: bool = False):
    module = resolve(ctx, module)
    if is_entry and module.entry is None:
        ctx.add_error_to_node(
            node=module,
            message="Module must have an entrypoint defined",
            hint="Use the 'entrypoint {}' construction"
        )
    module = builtins(ctx, module)
    module = typecheck(ctx, module)
    if ctx.has_errors():
        raise CompilationInterrupted()
    if not is_entry:
        module.entry = None
