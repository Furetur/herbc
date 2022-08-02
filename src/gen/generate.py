from llvmlite import ir

from src.ast import Module, AstVisitor
from src.defs.constants import LL_FILE_EXT
from src.env import Compiler
from src.gen.gen_visitor import GenVisitor


def generate(compiler: Compiler, mod: Module):
    visitor = GenVisitor(mod)
    visitor.visit(mod)

    outpath = compiler.project.build_dir() / (mod.name() + LL_FILE_EXT)
    with open(str(outpath), "w") as f:
        f.write(str(visitor.module))
