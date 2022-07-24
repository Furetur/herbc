import dataclasses
from typing import List

from src.ast.declarations import Import
from src.ast.node import Node

@dataclasses.dataclass()
class File(Node):
    """
    A parser's result
    """
    imports: List[Import]


class Module(Node):
    imports: List[Import]