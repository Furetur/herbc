import sys
from pathlib import Path

from src.defs.env import Project, Compiler
from src.defs.errs import CompilationInterrupted, Errors
from src.defs.pos import Pos
from src.load import load_entryfile
from src.parser.generated.HerbLexer import HerbLexer
from src.parser.generated.HerbParser import HerbParser
from src.parser.parser import parse


def main():
    compiler = Compiler(
        project=Project(root=Path("programs") / "proj1", root_packages=dict()),
        errors=Errors()
    )

    loaded = dict()
    try:
        load_entryfile(compiler, Path("programs") / "proj1" / "main.herb", loaded)
        print(loaded)
    except CompilationInterrupted as e:
        compiler.errors.print_errors()
        print(e)
        exit(1)


if __name__ == '__main__':
    main()