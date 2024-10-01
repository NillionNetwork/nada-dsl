"""Program Input Output utilities. 

Define the types used for inputs and outputs in Nada programs. 

"""

from dataclasses import dataclass
from typing import Any

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    InputASTOperation,
    LiteralASTOperation,
    next_operation_id,
)
from nada_dsl.errors import InvalidTypeError
from nada_dsl.nada_types import AllTypes, Party
from nada_dsl.nada_types import NadaType
from nada_dsl.source_ref import SourceRef


class Input(NadaType):
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
        self.id = next_operation_id()
        self.name = name
        self.party = party
        self.doc = doc
        self.inner = None
        self.source_ref = SourceRef.back_frame()
        super().__init__(self.inner)

    def store_in_ast(self, ty: object):
        """Store object in AST"""
        AST_OPERATIONS[self.id] = InputASTOperation(
            id=self.id,
            name=self.name,
            ty=ty,
            party=self.party,
            doc=self.doc,
            source_ref=self.source_ref,
        )


class Literal(NadaType):
    """
    Represents a literal value.

    Attributes:
        value (Any): The value of the literal.
    """

    value: Any
    source_ref: SourceRef

    def __init__(self, value, source_ref):
        self.id = next_operation_id()
        self.value = value
        self.source_ref = source_ref
        self.inner = None
        super().__init__(self.inner)

    def store_in_ast(self, ty: object):
        """Store object in AST"""
        AST_OPERATIONS[self.id] = LiteralASTOperation(
            operation_id=self.id,
            name=self.__class__.__name__,
            ty=ty,
            value=self.value,
            source_ref=self.source_ref,
        )


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
            raise InvalidTypeError(
                f"{self.source_ref.file}:{self.source_ref.lineno}: Output value "
                f"{inner} of type {type(inner)} is not "
                f"a Nada type so it isn't a valid output"
            )
        self.inner = inner
        self.name = name
        self.party = party
