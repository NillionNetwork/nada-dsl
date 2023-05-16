from dataclasses import dataclass

from nada_dsl.nada_types import AllTypes
from nada_dsl.source_ref import SourceRef


@dataclass
class Addition:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Subtraction:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Multiplication:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Division:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Modulo:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class RightShift:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class LeftShift:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class LessThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class GreaterThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class LessOrEqualThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class GreaterOrEqualThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Equals:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef
