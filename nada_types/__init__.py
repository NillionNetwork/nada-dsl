from dataclasses import dataclass
from typing import Union, Type

AllTypes = Union[
    "PublicBigInteger",
    "PublicBigUnsignedInteger",
    "PublicBoolean",
    "PublicFixedPointRational",
    "SecretBigInteger",
    "SecretBigUnsignedInteger",
    "SecretBoolean",
    "SecretFixedPointRational",
]
AllTypesType = Union[
    Type["PublicBigInteger"],
    Type["PublicBigUnsignedInteger"],
    Type["PublicBoolean"],
    Type["PublicFixedPointRational"],
    Type["SecretBigInteger"],
    Type["SecretBigUnsignedInteger"],
    Type["SecretBoolean"],
    Type["SecretFixedPointRational"],
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
