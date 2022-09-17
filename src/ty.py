from abc import ABC
from typing import List


class Ty(ABC):
    ...


class TyPrimitive(Ty):
    name: str

    def __init__(self, *, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, TyPrimitive) and self.name == other.name


TyUnknown = TyPrimitive(name="unknown")
TyVoid = TyPrimitive(name="void")
TyInt = TyPrimitive(name="int")
TyBool = TyPrimitive(name="bool")
TyStr = TyPrimitive(name="str")

ty_primitive_by_name = dict()

for ty in [TyVoid, TyInt, TyBool, TyStr]:
    ty_primitive_by_name[ty.name] = ty


class TyFunc(Ty):
    args: 'List[Ty]'
    ret: 'Ty'

    def __init__(self, *, args: 'List[Ty]', ret: 'Ty'):
        self.args = args
        self.ret = ret

    def __str__(self):
        return "(" + ", ".join(str(ty) for ty in self.args) + f") -> {self.ret}"
