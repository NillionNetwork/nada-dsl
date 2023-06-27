from dataclasses import dataclass
from typing import Union, Type

AllTypes = Union[
    "PublicInteger",
    "PublicUnsignedInteger",
    "PublicBoolean",
    "PublicRational",
    "SecretInteger",
    "SecretUnsignedInteger",
    "SecretBoolean",
    "SecretRational",
]
AllTypesType = Union[
    Type["PublicInteger"],
    Type["PublicUnsignedInteger"],
    Type["PublicBoolean"],
    Type["PublicRational"],
    Type["SecretInteger"],
    Type["SecretUnsignedInteger"],
    Type["SecretBoolean"],
    Type["SecretRational"],
]
OperationType = Union[
    "Addition",
    "Subtraction",
    "Multiplication",
    "Division",
    "Modulo",
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
]


@dataclass
class NadaType:
    inner: OperationType
