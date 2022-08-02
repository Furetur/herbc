import subprocess
from pathlib import Path
from typing import List

from src.defs.constants import LL_FILE_EXT
from src.env import Compiler
from src.errs import CompilationInterrupted


def make_executable(compiler: Compiler, outpath: Path):
    ll_files = [str(path.absolute()) for path in __get_all_ll_files(compiler)]
    code = subprocess.run(
        f"clang-14 {(' '.join(ll_files))} -o {str(outpath)}",
        cwd=Path.cwd(),
        shell=True
    ).returncode
    if code != 0:
        raise CompilationInterrupted("clang returned non-null exit code")


def __get_all_ll_files(compiler: Compiler) -> List[Path]:
    return list(compiler.project.build_dir().glob("*" + LL_FILE_EXT))