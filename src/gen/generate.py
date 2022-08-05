import subprocess
from pathlib import Path

from llvmlite import ir

from src.ast import Module, AstVisitor
from src.context.error_ctx import CompilationInterrupted
from src.defs.constants import LL_FILE_EXT
from src.context.compilation_ctx import CompilationCtx
from src.gen.gen_visitor import GenVisitor
from src.gen.make_executable import make_executable


def generate(compiler: CompilationCtx, mod: Module):
    visitor = GenVisitor(mod)
    visitor.visit(mod)

    ll_outpath = compiler.project.build_dir() / (mod.name() + LL_FILE_EXT)
    with open(str(ll_outpath), "w") as f:
        f.write(str(visitor.module))
    make_executable(compiler, [ll_outpath])
