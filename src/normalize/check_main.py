from typing import cast

from src.ast import Module, FunDecl
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted
from src.ty import TyVoid


def check_main(compiler: CompilationCtx, mod: Module):
    if "main" not in mod:
        compiler.add_error_to_node(
            node=mod,
            message="Entry module must have a 'main' function",
            hint="Define a main function: fn main() { }"
        )
        return
    decl = mod.get_declaration("main")
    if type(decl) is not FunDecl:
        compiler.add_error_to_node(
            node=decl,
            message="Entry module must have a 'main' function",
            hint="'main' is a reserved name for an entry point function"
        )
        return
    decl = cast(FunDecl, decl)
    if len(decl.args) != 0:
        compiler.add_error_to_node(
            node=decl,
            message="'main' function must not have any arguments",
            hint="'main' is a reserved name for an entry point function"
        )
    if decl.ret_ty != TyVoid:
        compiler.add_error_to_node(
            node=decl,
            message=f"'main' function must return void, but it returns {decl.ret_ty}",
            hint="'main' is a reserved name for an entry point function"
        )
