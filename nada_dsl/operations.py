"""
Class definitions corresponding to Nada operations.
"""
from dataclasses import dataclass
from typing import Generic, Optional

from nada_dsl import SourceRef
from nada_dsl.nada_types.collections import Array, Tuple
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
class PublicOutputEquality:
    left: AllTypes
    right: AllTypes
    source_ref: SourceRef

@dataclass
class Unzip:
    inner: OperationType
    source_ref: SourceRef

@dataclass
class Random:
    source_ref: SourceRef

@dataclass
class IfElse:
    '''
    cond.if_else(left, right)
    '''
    this: AllTypes  # cond
    arg_0: AllTypes # left
    arg_1: AllTypes # right
    source_ref: SourceRef

@dataclass
class Reveal:
    '''
    secret.reveal()
    '''
    this: AllTypes  # secret to reveal
    source_ref: SourceRef


def unzip(array: Array[Tuple[T, R]]) -> Tuple[Array[T], Array[R]]:
    right_type = Array.generic_type(array.inner_type.right_type, size=array.size)
    left_type = Array.generic_type(array.inner_type.left_type, size=array.size)

    return Tuple(
        right_type=right_type,
        left_type=left_type,
        inner=Unzip(inner=array, source_ref=SourceRef.back_frame()),
    )
