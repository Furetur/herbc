import subprocess
from pathlib import Path
from typing import List

from src.defs.constants import LL_FILE_EXT, BUILD_DIR_NAME
from src.context.compilation_ctx import CompilationCtx
from src.context.error_ctx import CompilationInterrupted


def make_executable(compiler: CompilationCtx, ll_files: List[Path]):
    ll_files = [str(path.absolute()) for path in (get_runtime_ll_files(compiler) + ll_files)]
    result = subprocess.run(
        f"clang-14 {(' '.join(ll_files))} -o {str(compiler.outpath)}",
        cwd=Path.cwd(),
        shell=True,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        raise CompilationInterrupted(f"clang returned non-null exit code:\n{result.stdout}\n{result.stderr}")


def get_runtime_ll_files(compiler: CompilationCtx) -> List[Path]:
    runtime_artifacts_dir = compiler.project.runtime / BUILD_DIR_NAME
    runtime_ll_files = list(runtime_artifacts_dir.glob("*" + LL_FILE_EXT))
    if len(runtime_ll_files) == 0:
        raise CompilationInterrupted(f"cannot find runtime artifacts in {runtime_artifacts_dir}")
    return runtime_ll_files
