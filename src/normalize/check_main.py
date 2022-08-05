from src.ast import Module, FunDecl
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted


def check_main(compiler: CompilationCtx, entry: Module):
    s = entry.scope
    if "main" not in s:
        compiler.add_error_to_node(
            node=entry,
            message="Entry module must have a 'main' function",
            hint="Define a main function: fn main() { }"
        )
        raise CompilationInterrupted()
    decl = s.get_declaration("main")
    if type(decl) is not FunDecl:
        compiler.add_error_to_node(
            node=decl,
            message="Entry module must have a 'main' function",
            hint="'main' is a reserved name for an entry point function"
        )
        raise CompilationInterrupted()