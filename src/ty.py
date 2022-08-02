import dataclasses


@dataclasses.dataclass(kw_only=True)
class Ty:
    pass


TyInt = Ty()
