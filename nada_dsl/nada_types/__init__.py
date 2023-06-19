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
    "Array",
    "Vector",
    "NadaTuple"
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
    Type["Array"],
    Type["Vector"],
    Type["NadaTuple"]
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
