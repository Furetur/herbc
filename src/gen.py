from pathlib import Path

from llvmlite import ir

from src.ast import Module
from src.defs.constants import LL_FILE_EXT
from src.env import Compiler

voidType = ir.VoidType()
intType = ir.IntType(32)
mainFnType = ir.FunctionType(intType, [])


def generate(compiler: Compiler, mod: Module):
    module = ir.Module(name=str(mod.path))
    module.triple = "x86_64-pc-linux-gnu"

    print_int_type = ir.FunctionType(voidType, [intType])
    print_int_fn = ir.Function(module, print_int_type, name="print_int")

    main_fn = ir.Function(module, mainFnType, name="main")
    block = main_fn.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.call(print_int_fn, [ir.Constant(intType, 1337)])
    builder.ret(ir.Constant(intType, 10))

    outpath = compiler.project.build_dir() / (mod.name() + LL_FILE_EXT)
    with open(str(outpath), "w") as f:
        f.write(str(module))
