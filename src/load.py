import dataclasses
from pathlib import Path
from typing import Dict, List
from os import listdir
from os.path import isfile, join, splitext

from src.ast.declarations import ImportPath
from src.ast.module import Module, File
from src.defs.constants import HERB_FILE_EXT
from src.defs.env import ProjectEnvironment
from src.parser.parser import parse


def load_entryfile(proj: ProjectEnvironment, path: ImportPath, loaded: Dict[Path, Module]) -> Module:
    resolved_path = path.abs_path(proj)
    assert resolved_path.is_file()
    file = parse(resolved_path)
    module = Module(imports=file.imports)
    loaded[resolved_path] = module
    # load recursively
    for imp in file.imports:
        load_package(proj, imp.import_path, loaded)
    return module


def load_package(proj: ProjectEnvironment, path: ImportPath, loaded: Dict[Path, Module]) -> Module:
    if not path.is_relative:
        raise "Absolute paths are not supported yet"
    resolved_path = path.abs_path(proj)
    assert resolved_path.is_dir()
    if resolved_path in loaded:
        return loaded[resolved_path]
    filenames = [f for f in listdir(str(resolved_path)) if isfile(join(str(resolved_path), f)) and splitext(f)[1] == HERB_FILE_EXT]
    parsed_files = [parse(resolved_path / name) for name in filenames]
    module = merge_files(parsed_files)
    loaded[resolved_path] = module
    # load recursively
    for imp in module.imports:
        load_package(proj, imp.import_path, loaded)
    return module


def merge_files(files: List[File]) -> Module:
    # collect all imports without repetitions
    imports = dict()
    for f in files:
        for imp in f.imports:
            imports[imp.import_path] = imp
    return Module(imports=list(imports.values()))
