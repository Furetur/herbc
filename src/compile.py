import subprocess
from pathlib import Path

from src.errs import CompilationInterrupted


def make_executable(llpath: Path, outpath: Path):
    code = subprocess.run(["clang-14", str(llpath), "-o", str(outpath)]).returncode
    if code != 0:
        raise CompilationInterrupted("clang returned non-null exit code")
