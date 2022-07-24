import sys
from pathlib import Path

from antlr4 import *

from src.ast.declarations import ImportPath
from src.defs.env import ProjectEnvironment
from src.load import load_entryfile
from src.parser.generated.HerbLexer import HerbLexer
from src.parser.generated.HerbParser import HerbParser
from src.parser.parser import parse


def main():
    proj = ProjectEnvironment(root=Path("programs") / "proj1", root_packages=dict())
    main_import = ImportPath(is_relative=True, path=["main.herb"])
    loaded = dict()
    load_entryfile(proj, main_import, loaded)
    print(loaded)


if __name__ == '__main__':
    main()