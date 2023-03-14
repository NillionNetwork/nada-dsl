from dataclasses import dataclass

from nada_dsl.nada_types import AllTypes

from nada_dsl.source_ref import SourceRef


class Party:
    name: str
    source_ref: SourceRef

    def __init__(self, name):
        self.name = name
        self.source_ref = SourceRef.back_frame()


class Input:
    party: Party
    name: str
    doc: str
    source_ref: SourceRef

    def __init__(self, name, party, doc=""):
        self.name = name
        self.party = party
        self.doc = doc
        self.source_ref = SourceRef.back_frame()


@dataclass
class Output:
    inner: AllTypes
    party: Party
    name: str
    source_ref: SourceRef

    def __init__(self, inner, name, party):
        self.inner = inner
        self.name = name
        self.party = party
        self.source_ref = SourceRef.back_frame()
