from nada_types import AllTypes


class Addition:
    right: AllTypes
    left: AllTypes
    lineno: str
    file: str

    def __init__(self, right, left, back_stackframe):
        self.lineno = back_stackframe.f_lineno
        self.file = back_stackframe.f_code.co_filename
        self.right = right
        self.left = left


class Multiplication:
    right: AllTypes
    left: AllTypes
    lineno: str
    file: str

    def __init__(self, right, left, back_stackframe):
        self.lineno = back_stackframe.f_lineno
        self.file = back_stackframe.f_code.co_filename
        self.right = right
        self.left = left
