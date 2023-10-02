"""Operation definitions."""
from dataclasses import dataclass
from typing import Generic, Optional

from nada_dsl import SourceRef
from nada_dsl.nada_types.collections import Array, NadaTuple
from nada_dsl.nada_types.function import NadaFunction
from nada_dsl.nada_types.generics import T, R
from nada_dsl.nada_types import AllTypes, OperationType


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
class Power:
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


@dataclass
class Unzip:
    inner: OperationType
    source_ref: SourceRef


def unzip(array: Array[NadaTuple[T, R]]) -> NadaTuple[Array[T], Array[R]]:
    right_type = Array.generic_type(array.inner_type.right_type, size=array.size)
    left_type = Array.generic_type(array.inner_type.left_type, size=array.size)

    return NadaTuple(
        right_type=right_type,
        left_type=left_type,
        inner=Unzip(inner=array, source_ref=SourceRef.back_frame()),
    )
