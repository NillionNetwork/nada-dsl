from dataclasses import dataclass
from inspect import currentframe

from nada_types import AllTypes


class Party:
    name: str
    lineno: str
    file: str

    def __init__(self, name):
        back_stackframe = currentframe().f_back
        self.lineno = back_stackframe.f_lineno
        self.file = back_stackframe.f_code.co_filename
        self.name = name


class Input:
    party: Party
    name: str
    lineno: str
    file: str

    def __init__(self, name, party):
        back_stackframe = currentframe().f_back
        self.lineno = back_stackframe.f_lineno
        self.file = back_stackframe.f_code.co_filename
        self.name = name
        self.party = party


@dataclass
class Output:
    inner: AllTypes
    name: str
    lineno: int
    file: str

    def __init__(self, inner, name):
        self.inner = inner
        self.name = name
        back_stackframe = currentframe().f_back
        self.lineno = back_stackframe.f_lineno
        self.file = back_stackframe.f_code.co_filename
