from dataclasses import dataclass

from . import NadaType


class StringEncodingCompare:
    pass


@dataclass
class SecretString(NadaType):
    encoding: StringEncodingCompare

@dataclass
class PublicString(NadaType):
    encoding: StringEncodingCompare
