from pathlib import Path

from src.compile import make_executable
from src.env import Project, Compiler
from src.errs import CompilationInterrupted, Errors
from src.gen import generate
from src.loader import Loader

root = Path("programs") / "proj1"
inpath = root / "main.herb"
llpath = Path("experiments") / "main.ll"
outpath = Path("experiments") / "main"

def main():
    compiler = Compiler(
        project=Project(root=Path("programs") / "proj1", root_packages=dict()),
        errors=Errors()
    )
    loader = Loader(compiler)

    try:
        entry = loader.load_file(Path("programs") / "proj1" / "main.herb")
        generate(entry, llpath)
        make_executable(llpath, outpath)

    except CompilationInterrupted as e:
        compiler.errors.print_errors()
        print(e)
        exit(1)


if __name__ == '__main__':
    main()