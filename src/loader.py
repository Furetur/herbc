import os.path
from pathlib import Path
from typing import Dict, List

from src.ast import Import, Module
from src.defs.constants import HERB_FILE_EXT
from src.env import Compiler
from src.errs import CompilationInterrupted
from src.span import INVALID_SPAN
from src.parser import parse


class Loader:
    compiler: Compiler
    __loaded: Dict[Path, Module]

    def __init__(self, compiler: Compiler):
        self.compiler = compiler
        self.__loaded = dict()

    def get_loaded_modules(self) -> List[Module]:
        """
        Topologically sorts the modules
        :return:
        """
        pass

    def load_file(self, path: Path) -> Module:
        if not path.is_file():
            raise CompilationInterrupted(f"File not found: {path}")
        module = parse(self.compiler, path)
        self.__loaded[path] = module
        self.__load_imported(module)
        return module

    def __load_imported(self, module: Module):
        for imp in module.imports:
            self.__load_import(imp)

    def __load_import(self, i: Import):
        path = self.__resolve_path(i)
        if not path.is_file():
            self.compiler.add_error_to_node(i, f"File not found {i.import_path()}",
                                            f"path was resolved as {path.absolute()}")
            raise CompilationInterrupted()
        i.imported_module = self.load_file(path)

    def __resolve_path(self, i: Import) -> Path:
        assert len(i.path) > 0

        if i.is_relative:
            root = self.compiler.project.root
        else:
            root_package = i.path[0]
            if root_package not in self.compiler.project.root_packages:
                self.compiler.add_error_to_node(
                    node=i,
                    message=f"Root package '{root_package}' could not be resolved in '{i.import_path()}'",
                    hint=f"This is an absolute import. It is resolved relative to the first package in the path, '{root_package}'. "
                         f"If you wanted a relative import then try '.{i.import_path()}' or define the root package."
                )
                raise CompilationInterrupted()
            root = self.compiler.project.root_packages[i.path[0]]

        path_tail = ""
        for p in (i.path if i.is_relative else i.path[1:]):
            path_tail = os.path.join(path_tail, p)

        return root / (path_tail + HERB_FILE_EXT)
