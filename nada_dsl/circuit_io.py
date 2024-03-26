from dataclasses import dataclass
from typing import Any

from nada_dsl.nada_types import AllTypes, NadaType

from nada_dsl.source_ref import SourceRef


class Party:
    """
    Represents a party involved in the computation.

    Attributes:
        name (str): The name of the party.
    """

    name: str
    source_ref: SourceRef

    def __init__(self, name):
        self.name = name
        self.source_ref = SourceRef.back_frame()


class Input:
    """
    Represents an input to the computation.

    Attributes:
        name (str): The name of the input.
        party (Party): The party providing the input.
        doc (str): Documentation for the input (default "").
    """

    name: str
    party: Party
    doc: str
    source_ref: SourceRef

    def __init__(self, name, party, doc=""):
        self.name = name
        self.party = party
        self.doc = doc
        self.source_ref = SourceRef.back_frame()


class Literal:
    """
    Represents a literal value.

    Attributes:
        value (Any): The value of the literal.
    """

    value: Any
    source_ref: SourceRef

    def __init__(self, value, source_ref):
        self.value = value
        self.source_ref = source_ref


@dataclass
class Output:
    """
    Represents an output from the computation.

    Attributes:
        inner (AllTypes): The type of the output.
        party (Party): The party receiving the output.
        name (str): The name of the output.
    """

    inner: AllTypes
    party: Party
    name: str
    source_ref: SourceRef

    def __init__(self, inner, name, party):
        self.source_ref = SourceRef.back_frame()
        if not issubclass(type(inner), NadaType):
            raise Exception(
                f"{self.source_ref.file}:{self.source_ref.lineno}: Output value {inner} of type {type(inner)} is not "
                f"a Nada type so it isn't a valid output")
        self.inner = inner
        self.name = name
        self.party = party
