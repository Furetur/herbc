import dataclasses
import subprocess
from pathlib import Path
from typing import List
from llvmlite import ir

from src.ast import Module, AstVisitor
from src.defs.constants import LL_FILE_EXT
from src.context.compilation_ctx import CompilationCtx
from src.gen.gen_visitor import GenVisitor
from src.gen.make_executable import make_executable


def generate(ctx: CompilationCtx, modules: List[Module]):
    ll_files = []
    for m in modules:
        ll_file = generate_module(ctx, m)
        ll_files.append(ll_file)
    make_executable(ctx, ll_files)


def generate_module(ctx: CompilationCtx, mod: Module) -> Path:
    ll_module = GenVisitor(ctx, mod).generate()
    ll_outpath = ctx.project.build_dir() / (mod.name + LL_FILE_EXT)
    with open(str(ll_outpath), "w") as f:
        f.write(str(ll_module))
    return ll_outpath
