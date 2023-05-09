from dataclasses import dataclass

from nada_dsl.nada_types import AllTypes
from nada_dsl.source_ref import SourceRef


@dataclass
class Addition:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Multiplication:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class CompareLessThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef
