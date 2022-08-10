import dataclasses


@dataclasses.dataclass(kw_only=True)
class Ty:
    name: str

    def __str__(self):
        return self.name


TyUnknown = Ty(name="unknown")
TyVoid = Ty(name="void")
TyInt = Ty(name="int")
TyBool = Ty(name="bool")
TyStr = Ty(name="str")
