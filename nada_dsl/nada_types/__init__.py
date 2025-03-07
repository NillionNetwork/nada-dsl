"""Nada type definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, TypeAlias, Union, Type
from nada_dsl.source_ref import SourceRef


@dataclass
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


AllTypes = Union[
    "Integer",
    "UnsignedInteger",
    "Boolean",
    "PublicInteger",
    "PublicUnsignedInteger",
    "PublicBoolean",
    "SecretInteger",
    "SecretUnsignedInteger",
    "SecretBoolean",
    "Array",
    "Tuple",
    "NTuple",
    "Object",
    "EcdsaPrivateKey",
    "EcdsaPublicKey",
    "EcdsaDigestMessage",
    "EcdsaSignature",
    "EddsaPrivateKey",
    "EddsaPublicKey",
    "EddsaMessage",
    "EddsaSignature",
]
AllTypesType = Union[
    Type["Integer"],
    Type["UnsignedInteger"],
    Type["Boolean"],
    Type["PublicInteger"],
    Type["PublicUnsignedInteger"],
    Type["PublicBoolean"],
    Type["SecretInteger"],
    Type["SecretUnsignedInteger"],
    Type["SecretBoolean"],
    Type["Array"],
    Type["ArrayType"],
    Type["Tuple"],
    Type["NTuple"],
    Type["Object"],
    Type["EcdsaPrivateKey"],
    Type["EcdsaPublicKey"],
    Type["EcdsaDigestMessage"],
    Type["EcdsaSignature"],
    Type["EddsaPrivateKey"],
    Type["EddsaPublicKey"],
    Type["EddsaMessage"],
    Type["EddsaSignature"],
]
OperationType = Union[
    "Addition",
    "Subtraction",
    "Multiplication",
    "Division",
    "Modulo",
    "Power",
    "RightShift",
    "LeftShift",
    "LessThan",
    "GreaterThan",
    "LessOrEqualThan",
    "GreaterOrEqualThan",
    "Equals",
    "Input",
    "Cast",
    "Map",
    "Zip",
    "Reduce",
    "Unzip",
    "Literal",
]

""
DslTypeRepr: TypeAlias = str | Dict[str, Dict]
"""Type alias for the NadaType representation. 

This representation can be either a string ("SecretInteger") 
or a dictionary (Array{contained_types=SecretInteger, size=3}).
"""


class Mode(Enum):
    """The mode of a type"""

    CONSTANT = 1
    PUBLIC = 2
    SECRET = 3


class BaseType(Enum):
    """The base type of a scalar type."""

    BOOLEAN = 1
    INTEGER = 2
    UNSIGNED_INTEGER = 3

    def is_numeric(self) -> bool:
        """Returns true if the base type is numeric."""
        return self in (BaseType.INTEGER, BaseType.UNSIGNED_INTEGER)


# TODO: abstract?
@dataclass
class DslType:
    """Nada type class.

    This is the parent class of all nada types.

    In Nada, all the types wrap Operations. For instance, an addition between two integers
    is represented like this SecretInteger(child=Addition(...)).

    In MIR, the representation is based around operations. A MIR operation points to other
    operations and has a return type.

    To aid MIR conversion, we store in memory (`AST_OPERATIONS`) all the operations in a
    MIR-friendly format, as subclasses of ASTOperation.

    Whenever the Python interpreter constructs an instance of NadaType, it will also store
    in memory the corresponding child operation. In order to do so, the ASTOperation will
    need the type in MIR format. Which is why all instances of `NadaType` provide an implementation
    of `to_mir()`.

    """

    child: OperationType

    def __init__(self, child: OperationType):
        """NadaType default constructor

        Args:
            child (OperationType): The child operation of this Data type
        """
        self.child = child
        if self.child is not None:
            self.child.store_in_ast(self.type().to_mir())

    def __bool__(self):
        raise NotImplementedError

    @classmethod
    def is_scalar(cls) -> bool:
        """Returns True if the type is a scalar."""
        return False

    @classmethod
    def is_literal(cls) -> bool:
        """Returns True if the type is a literal."""
        return False

    @abstractmethod
    def type(self):
        """Returns a meta type for this NadaType."""
