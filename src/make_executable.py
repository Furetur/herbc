import subprocess
from pathlib import Path
from typing import List

from src.defs.constants import LL_FILE_EXT, BUILD_DIR_NAME
from src.env import Compiler
from src.errs import CompilationInterrupted


def make_executable(compiler: Compiler, outpath: Path):
    ll_files = [str(path.absolute()) for path in get_all_ll_files(compiler)]
    result = subprocess.run(
        f"clang-14 {(' '.join(ll_files))} -o {str(outpath)}",
        cwd=Path.cwd(),
        shell=True,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        raise CompilationInterrupted(f"clang returned non-null exit code:\n{result.stdout}\n{result.stderr}")


def get_all_ll_files(compiler: Compiler) -> List[Path]:
    runtime_artifacts_dir = compiler.project.runtime / BUILD_DIR_NAME
    runtime_ll_files = list(runtime_artifacts_dir.glob("*" + LL_FILE_EXT))
    if len(runtime_ll_files) == 0:
        raise CompilationInterrupted(f"cannot find runtime artifacts in {runtime_artifacts_dir}")
    project_ll_files = list(compiler.project.build_dir().glob("*" + LL_FILE_EXT))
    return runtime_ll_files + project_ll_files
