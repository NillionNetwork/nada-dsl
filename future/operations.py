from nada_types import AllTypes, AllTypesType


class Cast:
    target: AllTypes
    to: AllTypesType
    lineno: str
    file: str

    def __init__(self, target, to, back_stackframe):
        self.lineno = back_stackframe.f_lineno
        self.file = back_stackframe.f_code.co_filename
        self.target = target
        self.to = to
