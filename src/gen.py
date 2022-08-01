from pathlib import Path

from llvmlite import ir

from src.ast import Module


intType = ir.IntType(32)
mainFnType = ir.FunctionType(intType, [])


def generate(mod: Module, outpath: Path):
    module = ir.Module(name=str(mod.path))
    module.triple = "x86_64-pc-linux-gnu"

    mainFn = ir.Function(module, mainFnType, name="main")
    block = mainFn.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    builder.ret(ir.Constant(intType, 10))

    with open(str(outpath), "w") as f:
        f.write(str(module))
