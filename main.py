import os.path
import sys
from pathlib import Path
from argparse import ArgumentParser

from src.defs.constants import RUNTIME_DIR_NAME
from src.make_executable import make_executable
from src.env import Project, Compiler
from src.errs import CompilationInterrupted, Errors
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

    run_compiler(entry_file_path, output_file_path, runtime_path)


def run_compiler(filepath: Path, outpath: Path, runtime_path: Path):
    compiler = Compiler(
        project=Project(root=filepath.parent, root_packages=dict(), runtime=runtime_path),
        errors=Errors()
    )
    loader = Loader(compiler)

    compiler.project.build_dir().mkdir(exist_ok=True)
    try:
        entry = loader.load_file(filepath)
        generate(compiler, entry)
        make_executable(compiler, outpath)
    except CompilationInterrupted as e:
        compiler.errors.print_errors()
        print("ERROR:", end=" ")
        print(e)
        exit(1)


if __name__ == '__main__':
    main()
