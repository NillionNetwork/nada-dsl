import copy
from dataclasses import dataclass
from typing import Generic, Optional
import typing

from nada_dsl.source_ref import SourceRef
from nada_dsl.errors import NadaNotAllowedException
from nada_dsl.nada_types.function import NadaFunction
from nada_dsl.nada_types.generics import U, T, R
from . import NadaType, AllTypesType, OperationType


@dataclass
class Map(Generic[T, R]):
    inner: OperationType
    fn: NadaFunction[T, R]
    source_ref: SourceRef


@dataclass
class Zip:
    left: OperationType
    right: OperationType
    source_ref: SourceRef


@dataclass
class Reduce(Generic[T, R]):
    inner: OperationType
    fn: NadaFunction[T, R]
    initial: R
    source_ref: SourceRef


@dataclass
class TupleType:
    left_type: AllTypesType
    right_type: AllTypesType


@dataclass
class TupleNew(Generic[T, U]):
    inner_type: AllTypesType
    inner: typing.Tuple[T, U]
    source_ref: SourceRef


@dataclass
class Tuple(Generic[T, U], NadaType):
    left_type: T
    right_type: U

    @classmethod
    def new(cls, left_type: T, right_type: U) -> "Tuple[T, U]":
        return Tuple(
            left_type=left_type,
            right_type=right_type,
            inner=TupleNew(
                inner=(left_type, right_type),
                source_ref=SourceRef.back_frame(),
                inner_type=Tuple(left_type=left_type, right_type=right_type, inner=None),
            ),
        )

    @classmethod
    def generic_type(cls, left_type: U, right_type: T) -> TupleType:
        return TupleType(left_type=left_type, right_type=right_type)


def get_inner_type(inner_type):
    inner_type = copy.copy(inner_type)
    setattr(inner_type, "inner", None)
    return inner_type


@dataclass
class ArrayType:
    inner_type: AllTypesType
    size: int


@dataclass
class ArrayNew(Generic[T]):
    inner_type: AllTypesType
    inner: [T]
    source_ref: SourceRef


@dataclass
class Array(Generic[T], NadaType):
    """
    Arrays have fixed size at compile time.
    """

    inner_type: T
    size: int
    
    def __init__(self, inner, size, inner_type=None):
        self.inner_type = (
            inner_type if not inner or inner_type else get_inner_type(inner)
        )
        self.size = size
        self.inner = inner if inner_type else getattr(inner, "inner", None)

    def __iter__(self):
        raise NadaNotAllowedException(
            "Cannot iterate/for loop over a nada Array, use functional style Array functions instead (map, reduce, zip)"
        )

    def map(self: "Array[T]", function: NadaFunction[T, U]) -> "Array[U]":
        return Array(
            size=self.size,
            inner_type=function.return_type,
            inner=Map(inner=self, fn=function, source_ref=SourceRef.back_frame()),
        )

    def zip(self: "Array[T]", other: "Array[U]") -> "Array[Tuple[T, U]]":
        if self.size != other.size:
            raise Exception("Cannot zip arrays of different size")
        return Array(
            size=self.size,
            inner_type=Tuple.generic_type(self.inner_type, other.inner_type),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame()),
        )

    def reduce(self: "Array[T]", function: NadaFunction[T, R], initial: R) -> R:
        return function.return_type(
            Reduce(
                inner=self,
                fn=function,
                initial=initial,
                source_ref=SourceRef.back_frame(),
            )
        )

    @classmethod
    def new(cls, *args) -> "Array[T]":
        if not args:
            raise ValueError("At least one value is required")

        first_arg = args[0]
        if not all(isinstance(arg, type(first_arg)) for arg in args):
            raise TypeError("All arguments must be of the same type")

        return Array(
            inner_type=first_arg,
            size=len(args),
            inner=ArrayNew(
                inner=args,
                source_ref=SourceRef.back_frame(),
                inner_type=Array(inner_type=first_arg, size=len(args), inner=None),
            ),
        )

    @classmethod
    def generic_type(cls, inner_type: T, size: int) -> ArrayType:
        return ArrayType(inner_type=inner_type, size=size)

    @classmethod
    def init_as_template_type(cls, inner_type) -> "Array[T]":
        return Array(inner=None, inner_type=inner_type, size=None)


@dataclass
class VectorType:
    inner_type: AllTypesType


@dataclass
class Vector(Generic[T], NadaType):
    """
    Vector don't have fixed size at compile time but have it at runtime.
    """

    inner_type: T
    size: int

    def __init__(self, inner, size, inner_type=None):
        self.inner_type = (
            inner_type if not inner or inner_type else get_inner_type(inner)
        )
        self.size = size
        self.inner = inner if inner_type else getattr(inner, "inner", None)

    def __iter__(self):
        raise NadaNotAllowedException(
            "Cannot iterate/for loop over a nada Vector,"
            + " use functional style Vector functions instead (map, reduce, zip)"
        )

    def map(self: "Vector[T]", function: NadaFunction[T, R]) -> "Vector[R]":
        return Vector(
            size=self.size,
            inner_type=function.return_type,
            inner=(Map(inner=self, fn=function, source_ref=SourceRef.back_frame())),
        )

    def zip(self: "Vector[T]", other: "Vector[R]") -> "Vector[Tuple[T, R]]":
        return Vector(
            size=self.size,
            inner_type=Tuple.generic_type(self.inner_type, other.inner_type),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame()),
        )

    def reduce(
        self: "Vector[T]", function: NadaFunction[T, R], initial: Optional[R] = None
    ) -> R:
        return function.return_type(
            Reduce(
                inner=self,
                fn=function,
                initial=initial,
                source_ref=SourceRef.back_frame(),
            )
        )  # type: ignore

    @classmethod
    def generic_type(cls, inner_type: T) -> VectorType:
        return VectorType(inner_type=inner_type)

    @classmethod
    def init_as_template_type(cls, inner_type) -> "Vector[T]":
        return Vector(inner=None, inner_type=inner_type, size=None)
