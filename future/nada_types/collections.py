from dataclasses import dataclass
from typing import Generic, Tuple

from nada_dsl import SourceRef
from nada_dsl.future.nada_types.function import NadaFunction
from nada_dsl.future.nada_types.generics import U, T, R
from nada_dsl.future.nada_types.integer import PublicBigInteger
from nada_dsl.future.operations import Map, Zip, Reduce
from nada_dsl.nada_types import NadaType, AllTypesType


@dataclass
class NadaTupleType:
    right_type: AllTypesType
    left_type: AllTypesType


@dataclass
class NadaTuple(Generic[T, U], NadaType):
    right_type: U
    left_type: T

    @classmethod
    def generic_type(cls, rigth_type: U, left_type: T) -> NadaTupleType:
        return NadaTupleType(right_type=rigth_type, left_type=left_type)


@dataclass
class ArrayType:
    inner_type: AllTypesType
    size: int

@dataclass
class Array(Generic[T], NadaType):
    """
    Arrays have fixed size at compile time.
    """
    inner_type: T
    size: int

    def __init__(self, inner, size, inner_type=None):
        self.inner_type = inner_type if inner_type else type(inner)
        self.size = size
        self.inner = inner if inner_type else inner.inner

    def map(self: 'Array[T]', function: NadaFunction[T, U]) -> 'Array[U]':
        return Array(
            size=self.size,
            inner_type=function.return_type,
            inner=Map(inner=self, fn=function, source_ref=SourceRef.back_frame())
        )

    def zip(self: 'Array[T]', other: 'Array[U]') -> 'Array[NadaTuple[T, U]]':
        if self.size != other.size:
            raise Exception("Cannot zip arrays of different size")
        return Array(
            size=self.size,
            inner_type=NadaTuple.generic_type(self.inner_type, other.inner_type),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame())
        )

    def reduce(self: 'Array[T]', function: NadaFunction[T, R]) -> R:
        return function.return_type(Reduce(inner=self, fn=function, source_ref=SourceRef.back_frame()))

    @classmethod
    def generic_type(cls, inner_type: T, size: int) -> ArrayType:
        return ArrayType(inner_type=inner_type, size=size)


@dataclass
class VectorType:
    inner_type: AllTypesType


@dataclass
class Vector(Generic[T], NadaType):
    """
    Vector don't have fixed size at compile time but have it at runtime.
    """

    inner_type: T
    size: PublicBigInteger

    def __init__(self, inner, size, inner_type=None):
        self.inner_type = inner_type if inner_type else type(inner)
        self.size = size
        self.inner = inner if inner_type else inner.inner

    def map(self: 'Vector[T]', function: NadaFunction[T, R]) -> 'Vector[R]':
        return Vector(
            size=self.size,
            inner_type=function.return_type,
            inner=(Map(inner=self, fn=function, source_ref=SourceRef.back_frame()))
        )

    def zip(self: 'Vector[T]', other: 'Vector[R]') -> 'Vector[Tuple[T, R]]':
        return Vector(
            size=self.size,
            inner_type=NadaTuple.generic_type(self.inner_type, other.inner_type),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame())
        )

    def reduce(self: 'Vector[T]', function: NadaFunction[T, R]) -> R:
        return function.return_type(Reduce(inner=self, fn=function, source_ref=SourceRef.back_frame()))

    @classmethod
    def generic_type(cls, inner_type: T) -> VectorType:
        return VectorType(inner_type=inner_type)
