from dataclasses import dataclass

from nada_types import AllTypes


@dataclass
class Addition:
    right: AllTypes
    left: AllTypes
    lineno: str
    file: str


@dataclass
class Multiplication:
    right: AllTypes
    left: AllTypes
    lineno: str
    file: str
