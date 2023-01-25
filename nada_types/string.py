from dataclasses import dataclass

from . import NadaType


class StringEncodingCompare:
    pass


@dataclass
class String(NadaType):
    encoding: StringEncodingCompare
