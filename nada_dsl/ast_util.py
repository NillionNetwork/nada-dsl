""" AST utilities."""

from abc import ABC
from dataclasses import dataclass
import hashlib
from typing import Dict, List
from sortedcontainers import SortedDict
from nada_dsl.nada_types import NadaTypeRepr, Party
from nada_dsl.source_ref import SourceRef

OPERATION_ID_COUNTER = 0


def next_operation_id() -> int:
    """Returns the next value of the operation id counter."""
    global OPERATION_ID_COUNTER
    OPERATION_ID_COUNTER += 1
    return OPERATION_ID_COUNTER


@dataclass
class ASTOperation(ABC):
    """AST Operations.

    Base abstract class for all AST Operations. Defines the minimum contract
    that needs to be implemented by any subclass.

    Attributes
    ----------
    id: int
        The operation identifier. This is the unique identifier assigned by Python
        that is the return value of id().

    source_ref: SourceRef
        The source reference object

    ty: str | Dict[str, Dict]
        The type representation, it can be a string (e.g. "SecretInteger") or a dictionary
        for compount types.
    """

    id: int
    source_ref: SourceRef
    ty: NadaTypeRepr

    def inner_operations(self) -> List[int]:
        """Returns the list of identifiers of all the inner operations of this operation."""
        return []

    def to_mir(self):
        """Converts this AST Operation into a valid MIR data structure"""
        return {}


# Map of operations identified by the Python compiler
# The key is the operation identifier, the value the operation
AST_OPERATIONS: Dict[int, ASTOperation] = SortedDict()

# Map of literal hashes to index
LITERALS: Dict[str, int] = {}


@dataclass
class BinaryASTOperation(ASTOperation):
    """Superclass of all the Binary operations in AST representation"""

    name: str
    left: int
    right: int

    def inner_operations(self) -> List[int]:
        return [self.left, self.right]

    def to_mir(self):
        return {
            self.name: {
                "id": self.id,
                "left": self.left,
                "right": self.right,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class UnaryASTOperation(ASTOperation):
    """Superclass of all the unary operations in AST representation"""

    name: str
    inner: int

    def inner_operations(self):
        return [self.inner]

    def to_mir(self):

        return {
            self.name: {
                "id": self.id,
                "this": self.inner,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class IfElseASTOperation(ASTOperation):
    """AST Representation of an IfElse operation."""

    this: int
    arg_0: int
    arg_1: int

    def inner_operations(self):
        return [self.this, self.arg_0, self.arg_1]

    def to_mir(self):
        return {
            "IfElse": {
                "id": self.id,
                "this": self.this,
                "arg_0": self.arg_0,
                "arg_1": self.arg_1,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class RandomASTOperation(ASTOperation):
    """AST Representation of a Random operation."""

    def inner_operations(self):
        return []

    def to_mir(self):
        return {
            "Random": {
                "id": self.id,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class InputASTOperation(ASTOperation):
    """AST representation of an Input."""

    name: str
    party: Party
    doc: str

    def to_mir(self):
        return {
            "InputReference": {
                "id": self.id,
                "refers_to": self.name,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class LiteralASTOperation(ASTOperation):
    """AST Representation of a Literal."""

    name: str
    value: object
    literal_index: str

    def __init__(
        self,
        operation_id: int,
        name: str,
        ty: str | Dict[str, Dict],
        value: object,
        source_ref: SourceRef,
    ):
        self.id = operation_id
        self.name = name
        self.ty = ty
        self.value = value
        self.source_ref = source_ref
        # Generate a unique name depending on the value and type
        # to prevent duplicating literals in the bytecode.
        literal_name = hashlib.md5(
            (str(self.value) + str(self.ty)).encode("UTF-8")
        ).hexdigest()

        # Replace the literal name by an index so it is shorter
        if literal_name not in LITERALS:
            LITERALS[literal_name] = len(LITERALS)

        self.literal_index = str(LITERALS[literal_name])

        super().__init__(id=self.id, source_ref=self.source_ref, ty=self.ty)

    def to_mir(self):
        return {
            "LiteralReference": {
                "id": self.id,
                "refers_to": self.literal_index,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class ReduceASTOperation(ASTOperation):
    """AST Representation of a Reduce operation."""

    inner: int
    fn: int
    initial: int

    def inner_operations(self):
        return [self.inner, self.initial]

    def to_mir(self):
        return {
            "Reduce": {
                "id": self.id,
                "fn": self.fn,
                "inner": self.inner,
                "initial": self.initial,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class MapASTOperation(ASTOperation):
    """AST representation of a Map operation."""

    inner: int
    fn: int

    def inner_operations(self):
        return [self.inner]

    def to_mir(self):
        return {
            "Map": {
                "id": self.id,
                "fn": self.fn,
                "inner": self.inner,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class NewASTOperation(ASTOperation):
    """AST Representation of a New operation."""

    name: str
    elements: List[int]
    inner_type: object

    def inner_operations(self):
        return self.elements

    def to_mir(self):
        return {
            "New": {
                "id": self.id,
                "elements": self.elements,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class NadaFunctionCallASTOperation(ASTOperation):
    """AST representation of a NadaFunctionCall operation."""

    args: List[int]
    fn: int

    def inner_operations(self):
        return self.args

    def to_mir(self):
        return {
            "NadaFunctionCall": {
                "id": self.id,
                "function_id": self.fn,
                "args": self.args,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
                "return_type": self.ty,
            }
        }


@dataclass
class NadaFunctionArgASTOperation(ASTOperation):
    """AST representation of a NadaFunctionArg operation."""

    name: str
    fn: int

    def to_mir(self):
        return {
            "NadaFunctionArgRef": {
                "id": self.id,
                "function_id": self.fn,
                "refers_to": self.name,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }


@dataclass
class NadaFunctionASTOperation(ASTOperation):
    """AST representation of a nada function."""

    name: str
    args: List[int]
    inner: int

    # pylint: disable=arguments-differ
    def to_mir(self, operations):
        """Convert a function to MIR."""
        arg_operations: List[NadaFunctionArgASTOperation] = [
            AST_OPERATIONS[arg] for arg in self.args
        ]  # type: ignore

        return {
            "id": self.id,
            "args": [
                {
                    "name": arg.name,
                    "type": arg.ty,
                    "source_ref_index": arg.source_ref.to_index(),
                }
                for arg in arg_operations
            ],
            "function": self.name,
            "return_operation_id": self.inner,
            "operations": operations,
            "return_type": self.ty,
            "source_ref_index": self.source_ref.to_index(),
        }

    def __hash__(self) -> int:
        return self.id


# Partially implemented
@dataclass
class CastASTOperation(ASTOperation):
    """AST Representation of a Cast operation."""

    target: int

    def inner_operations(self):
        return [self.target]

    def to_mir(self):
        return {
            "Cast": {
                "id": self.id,
                "target": self.target,
                "to": self.ty,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }
