import os.path
import sys
from pathlib import Path
from argparse import ArgumentParser

from src.defs.constants import RUNTIME_DIR_NAME
from src.normalize import normalize
from src.context.compilation_ctx import CompilationCtx
from src.context.project_ctx import ProjectCtx
from src.context.error_ctx import CompilationInterrupted, ErrorCtx
from src.gen.generate import generate
from src.loader import Loader


def main():
    argparser = ArgumentParser(prog="herbc", description="Herb Compiler")
    argparser.add_argument("herb_file")
    argparser.add_argument("output_file", nargs="?")

    args = argparser.parse_args(sys.argv[1:])
    entry_file_path = Path(args.herb_file)

    if not entry_file_path.is_file():
        print(f"ERROR: {entry_file_path}: File not found")
        exit(1)

    if args.output_file is not None:
        output_file_path = Path(args.output_file)
    else:
        output_file_path = entry_file_path.parent / entry_file_path.stem

    runtime_path = Path(os.path.abspath(__file__)).parent / RUNTIME_DIR_NAME

    ok = run_compiler(entry_file_path, output_file_path, runtime_path)
    if not ok:
        exit(1)


def run_compiler(filepath: Path, outpath: Path, runtime_path: Path) -> bool:
    compiler = CompilationCtx(
        project=ProjectCtx(root=filepath.parent, root_packages=dict(), runtime=runtime_path),
        errors=ErrorCtx(),
        outpath=outpath,
    )
    loader = Loader(compiler)

    compiler.project.build_dir().mkdir(exist_ok=True)
    try:
        entry = loader.load_file(filepath)
        normalize(compiler, entry)
        generate(compiler, entry)
    except CompilationInterrupted as e:
        compiler.errors.print_errors()
        if e.message != "":
            print(f"ERROR: {e.message}")
        else:
            print("Compilation failed!")
        return False
    return True


if __name__ == '__main__':
    main()
