from pathlib import Path

from src.env import Project, Compiler
from src.errs import CompilationInterrupted, Errors
from src.loader import Loader



def main():
    compiler = Compiler(
        project=Project(root=Path("programs") / "proj1", root_packages=dict()),
        errors=Errors()
    )
    loader = Loader(compiler)

    try:
        loader.load_file(Path("programs") / "proj1" / "main.herb")
        print(loader.get_loaded())
    except CompilationInterrupted as e:
        compiler.errors.print_errors()
        print(e)
        exit(1)


if __name__ == '__main__':
    main()