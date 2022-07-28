import dataclasses
from pathlib import Path
from typing import Dict, List
from os import listdir
from os.path import isfile, join, splitext

from src.ast.declarations import Import
from src.ast.module import Module, File
from src.defs.constants import HERB_FILE_EXT
from src.defs.env import Compiler
from src.defs.errs import CompilationInterrupted
from src.parser.parser import parse

Loaded = Dict[Path, Module]


def load_entryfile(compiler: Compiler, path: Path, loaded: Loaded) -> Module:
    if not path.is_file():
        raise CompilationInterrupted(f"File not found: {path}")
    file = parse(compiler, path)
    module = Module(imports=file.imports)
    loaded[path] = module
    load_imported_packages(compiler, module, loaded)
    return module


def load_imported_packages(compiler: Compiler, module: Module, loaded: Loaded):
    for imp in module.imports:
        path = resolve_path(compiler, imp)
        if not path.is_dir():
            compiler.add_error_to_node(imp, f"Package not found {imp.import_path()}", f"path was resolved as {path}")
            raise CompilationInterrupted()
        load_package(compiler, path, loaded)


def load_package(compiler: Compiler, path: Path, loaded: Dict[Path, Module]) -> Module:
    assert path.is_dir()
    if path in loaded:
        return loaded[path]
    filenames = [f for f in listdir(str(path)) if isfile(join(str(path), f)) and splitext(f)[1] == HERB_FILE_EXT]
    parsed_files = [parse(compiler, path / name) for name in filenames]
    module = merge_files(compiler, parsed_files)
    loaded[path] = module
    load_imported_packages(compiler, module, loaded)
    return module


def merge_files(compiler: Compiler, files: List[File]) -> Module:
    # collect all imports without repetitions
    imports = dict()
    for f in files:
        for imp in f.imports:
            imports[resolve_path(compiler, imp)] = imp
    return Module(imports=list(imports.values()))


def resolve_path(compiler: Compiler, i: Import) -> Path:
    assert len(i.path) > 0 or i.is_relative

    if len(i.path) == 0:
        i.resolved_path = compiler.project.root
    else:
        if i.is_relative:
            root = compiler.project.root
        else:
            root_package = i.path[0]
            if root_package not in compiler.project.root_packages:
                compiler.add_error_to_node(
                    node=i,
                    message=f"Root package '{root_package}' could not be resolved in '{i.import_path()}'",
                    hint=f"This is an absolute import. It is resolved relative to the first package in the path, '{root_package}'. "
                         f"If you wanted a relative import then try '.{i.import_path()}' or define the root package."
                )
                raise CompilationInterrupted()
            root = compiler.project.root_packages[i.path[0]]
        path_tail = Path("")
        for p in (i.path if i.is_relative else i.path[1:]):
            path_tail = path_tail / p
        i.resolved_path = root / path_tail
    return i.resolved_path
