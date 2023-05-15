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
class CompareLessThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class CompareGreaterThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class CompareLessOrEqualThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class CompareGreaterOrEqualThan:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef


@dataclass
class Equals:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef
