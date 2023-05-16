from dataclasses import dataclass
from typing import Union, Type

AllTypes = Union[
    "PublicInteger8",
    "PublicInteger16",
    "PublicBigInteger",
    "PublicUnsignedInteger8",
    "PublicUnsignedInteger16",
    "PublicBigUnsignedInteger",
    "PublicBoolean",
    "PublicFixedPointRational",
    "SecretInteger8",
    "SecretInteger16",
    "SecretBigInteger",
    "SecretUnsignedInteger8",
    "SecretUnsignedInteger16",
    "SecretBigUnsignedInteger",
    "SecretBoolean",
    "SecretFixedPointRational",
]
AllTypesType = Union[
    Type["PublicInteger8"],
    Type["PublicInteger16"],
    Type["PublicBigInteger"],
    Type["PublicUnsignedInteger8"],
    Type["PublicUnsignedInteger16"],
    Type["PublicBigUnsignedInteger"],
    Type["PublicBoolean"],
    Type["PublicFixedPointRational"],
    Type["SecretInteger8"],
    Type["SecretInteger16"],
    Type["SecretBigInteger"],
    Type["SecretUnsignedInteger8"],
    Type["SecretUnsignedInteger16"],
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
