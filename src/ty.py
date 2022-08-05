import dataclasses


@dataclasses.dataclass(kw_only=True)
class Ty:
    name: str

    def __str__(self):
        return "int"


TyUnknown = Ty(name="unknown")
TyInt = Ty(name="int")
