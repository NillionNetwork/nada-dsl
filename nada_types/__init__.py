from dataclasses import dataclass
from typing import Union, Type

AllTypes = Union[
    "PublicInteger8",
    "PublicInteger16",
    "PublicBigInteger",
    "SecretInteger8",
    "SecretInteger16",
    "SecretBigInteger",
]
AllTypesType = Union[
    Type["PublicInteger8"],
    Type["PublicInteger16"],
    Type["PublicBigInteger"],
    Type["SecretInteger8"],
    Type["SecretInteger16"],
    Type["SecretBigInteger"],
]
OperationType = Union[
    "Addition", "Multiplication", "Input", "Cast", "Map", "Zip", "Reduce", "Unzip"
]


@dataclass
class NadaType:
    inner: OperationType
