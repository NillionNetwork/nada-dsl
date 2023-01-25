from dataclasses import dataclass

from nada_types import NadaType


class StringEncodingCompare:
    pass


@dataclass
class String(NadaType):
    encoding: StringEncodingCompare
