from dataclasses import dataclass
from typing import Union, Type

AllTypes = Union[
    "Integer",
    "UnsignedInteger",
    "Boolean",
    "PublicInteger",
    "PublicUnsignedInteger",
    "PublicBoolean",
    "PublicRational",
    "SecretInteger",
    "SecretUnsignedInteger",
    "SecretBoolean",
    "Array",
    "Vector",
    "Tuple",
]
AllTypesType = Union[
    Type["Integer"],
    Type["UnsignedInteger"],
    Type["Boolean"],
    Type["PublicInteger"],
    Type["PublicUnsignedInteger"],
    Type["PublicBoolean"],
    Type["PublicRational"],
    Type["SecretInteger"],
    Type["SecretUnsignedInteger"],
    Type["SecretBoolean"],
    Type["Array"],
    Type["Vector"],
    Type["Tuple"],
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


@dataclass
class NadaType:
    inner: OperationType
