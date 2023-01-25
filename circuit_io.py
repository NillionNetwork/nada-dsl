from dataclasses import dataclass
from inspect import currentframe

from nada_types import AllTypes
from util import get_back_file_lineno


class Party:
    name: str
    lineno: str
    file: str

    def __init__(self, name):
        self.name = name
        file_lineno = get_back_file_lineno()
        self.lineno = file_lineno["lineno"]
        self.file = file_lineno["file"]


class Input:
    party: Party
    name: str
    doc: str
    lineno: str
    file: str

    def __init__(self, name, party, doc=""):
        self.name = name
        self.party = party
        self.doc = doc
        file_lineno = get_back_file_lineno()
        self.lineno = file_lineno["lineno"]
        self.file = file_lineno["file"]


@dataclass
class Output:
    inner: AllTypes
    name: str
    lineno: int
    file: str

    def __init__(self, inner, name):
        self.inner = inner
        self.name = name
        file_lineno = get_back_file_lineno()
        self.lineno = file_lineno["lineno"]
        self.file = file_lineno["file"]
