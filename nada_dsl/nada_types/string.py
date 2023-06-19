from dataclasses import dataclass

from . import NadaType


@dataclass
class SecretString(NadaType):
    length: int


@dataclass
class PublicString(NadaType):
    length: int
