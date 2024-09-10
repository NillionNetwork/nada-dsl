import copy
from dataclasses import dataclass
import inspect
from typing import Generic, List, Optional
import typing
from typing import TypeVar

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    MapASTOperation,
    NewASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
)
from nada_dsl.nada_types import NadaType

# Wildcard import due to non-zero types
from nada_dsl.nada_types.types import *  # pylint: disable=W0614:wildcard-import
from nada_dsl.source_ref import SourceRef
from nada_dsl.errors import NadaNotAllowedException
from nada_dsl.nada_types.function import NadaFunction, nada_fn
from nada_dsl.nada_types.generics import U, T, R
from . import AllTypes, AllTypesType, NadaTypeRepr, OperationType


def is_primitive_integer(nada_type_str: str):
    """TODO: Autogenerate this method"""
    return (
        nada_type_str
        in (
            "Integer",
            "PublicInteger",
            "SecretInteger",
            "UnsignedInteger",
            "PublicUnsignedInteger",
            "SecretUnsignedInteger",
        ),
    )


class Collection(NadaType):
    """Superclass of collection types"""

    left_type: AllTypesType
    right_type: AllTypesType
    inner_type: AllTypesType

    def to_type(self):
        """Convert operation wrapper to a dictionary representing its type."""
        if isinstance(self, (Array, ArrayType)):
            size = {"size": self.size} if self.size else {}
            inner_type = self.retrieve_inner_type()
            return {"Array": {"inner_type": inner_type, **size}}
        elif isinstance(self, (Vector, VectorType)):
            inner_type = self.retrieve_inner_type()
            return {"Vector": {"inner_type": inner_type}}
        elif type(self) == Tuple or type(self) == TupleType:
            return {
                "Tuple": {
                    "left_type": (
                        self.left_type.to_type()
                        if isinstance(self.left_type, (NadaType, ArrayType, TupleType))
                        else self.left_type.class_to_type()
                    ),
                    "right_type": (
                        self.right_type.to_type()
                        if isinstance(self.right_type, (NadaType, ArrayType, TupleType))
                        else self.right_type.class_to_type()
                    ),
                }
            }

    def retrieve_inner_type(self):
        if isinstance(self.inner_type, TypeVar):
            return "T"
        elif inspect.isclass(self.inner_type):
            return self.inner_type.class_to_type()
        else:
            return self.inner_type.to_type()


class Map(Generic[T, R]):
    inner: OperationType
    fn: NadaFunction[T, R]
    source_ref: SourceRef

    def __init__(
        self,
        inner: OperationType,
        fn: NadaFunction[T, R],
        source_ref: SourceRef,
    ):
        self.id = id(self)
        self.inner = inner
        self.fn = fn
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        AST_OPERATIONS[self.id] = MapASTOperation(
            id=self.id,
            inner=self.inner.inner.id,
            fn=self.fn.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class Reduce(Generic[T, R]):
    inner: OperationType
    fn: NadaFunction[T, R]
    initial: R
    source_ref: SourceRef

    def __init__(
        self,
        inner: OperationType,
        fn: NadaFunction[T, R],
        initial: R,
        source_ref: SourceRef,
    ):
        self.id = id(self)
        self.inner = inner
        self.fn = fn
        self.initial = initial
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        AST_OPERATIONS[self.id] = ReduceASTOperation(
            id=self.id,
            inner=self.inner.inner.id,
            fn=self.fn.id,
            initial=self.initial.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class TupleType:
    """Marker type for Tuples."""

    left_type: NadaType
    right_type: NadaType

    def to_type(self):
        return {
            "Tuple": {
                "left_type": self.left_type.to_type(),
                "right_type": self.right_type.to_type(),
            }
        }


class Tuple(Generic[T, U], Collection):
    left_type: T
    right_type: U

    def __init__(self, inner, left_type: T, right_type: U):
        self.left_type = left_type
        self.right_type = right_type
        self.inner = inner
        super().__init__(self.inner)

    @classmethod
    def new(cls, left_type: T, right_type: U) -> "Tuple[T, U]":
        return Tuple(
            left_type=left_type,
            right_type=right_type,
            inner=TupleNew(
                inner=(left_type, right_type),
                source_ref=SourceRef.back_frame(),
                inner_type=Tuple(
                    left_type=left_type, right_type=right_type, inner=None
                ),
            ),
        )

    @classmethod
    def generic_type(cls, left_type: U, right_type: T) -> TupleType:
        return TupleType(left_type=left_type, right_type=right_type)


def get_inner_type(inner_type):
    inner_type = copy.copy(inner_type)
    setattr(inner_type, "inner", None)
    return inner_type


class Zip:
    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = id(self)
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            name="Zip",
            left=self.left.inner.id,
            right=self.right.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Unzip:
    def __init__(self, inner: AllTypes, source_ref: SourceRef):
        self.id = id(self)
        self.inner = inner
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        AST_OPERATIONS[self.id] = UnaryASTOperation(
            id=self.id,
            name="Unzip",
            inner=self.inner.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class InnerProduct:
    """Inner product of two arrays."""

    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = id(self)
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            name="InnerProduct",
            left=self.left.inner.id,
            right=self.right.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class ArrayType:
    """Marker type for arrays."""

    inner_type: AllTypesType
    size: int

    def to_type(self):
        return {"Array": {"inner_type": self.inner_type.to_type(), "size": self.size}}


class Array(Generic[T], Collection):
    """Nada Array collection.
    Arrays have fixed size at compile time.

    Attributes
    ----------
    inner_type: T
        The type of the array
    inner:
        The optional inner operation
    size: int
        The size of the array
    """

    inner_type: T
    size: int

    def __init__(self, inner, size: int, inner_type: T = None):
        self.inner_type = (
            inner_type
            if (inner is None or inner_type is not None)
            else get_inner_type(inner)
        )
        self.size = size
        self.inner = inner if inner_type is not None else getattr(inner, "inner", None)
        if self.inner is not None:
            self.inner.store_in_ast(self.to_type())

    def __iter__(self):
        raise NadaNotAllowedException(
            "Cannot iterate/for loop over a nada Array, use functional style Array functions instead (map, reduce, zip)"
        )

    def map(self: "Array[T]", function) -> "Array":
        nada_function = function
        if not isinstance(function, NadaFunction):
            nada_function = nada_fn(function)
        return Array(
            size=self.size,
            inner_type=nada_function.return_type,
            inner=Map(inner=self, fn=nada_function, source_ref=SourceRef.back_frame()),
        )

    def reduce(self: "Array[T]", function, initial: R) -> R:
        if not isinstance(function, NadaFunction):
            function = nada_fn(function)
        return function.return_type(
            Reduce(
                inner=self,
                fn=function,
                initial=initial,
                source_ref=SourceRef.back_frame(),
            )
        )

    def zip(self: "Array[T]", other: "Array[U]") -> "Array[Tuple[T, U]]":
        if self.size != other.size:
            raise Exception("Cannot zip arrays of different size")
        return Array(
            size=self.size,
            inner_type=Tuple(
                left_type=self.inner_type, right_type=other.inner_type, inner=None
            ),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame()),
        )

    def inner_product(self: "Array[T]", other: "Array[T]") -> T:
        if self.size != other.size:
            raise Exception("Cannot do inner product of arrays of different size")

        if is_primitive_integer(self.retrieve_inner_type()) and is_primitive_integer(
            other.retrieve_inner_type()
        ):
            callable = (
                self.inner_type
                if inspect.isclass(self.inner_type)
                else self.inner_type.__class__
            )
            return callable(
                inner=InnerProduct(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )  # type: ignore
        else:
            raise Exception(
                "Inner product is only implemented for arrays of integer types"
            )

    @classmethod
    def new(cls, *args) -> "Array[T]":
        if len(args) == 0:
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
                inner_type=ArrayType(inner_type=first_arg, size=len(args)),
            ),
        )

    @classmethod
    def generic_type(cls, inner_type: T, size: int) -> ArrayType:
        return ArrayType(inner_type=inner_type, size=size)

    @classmethod
    def init_as_template_type(cls, inner_type) -> "Array[T]":
        return Array(inner=None, inner_type=inner_type, size=None)


@dataclass
class VectorType(Collection):
    inner_type: AllTypesType


@dataclass
class Vector(Generic[T], Collection):
    """
    Vector don't have fixed size at compile time but have it at runtime.
    """

    inner_type: T
    size: int

    def __init__(self, inner, size, inner_type=None):
        self.inner_type = (
            inner_type
            if (inner is None or inner_type is not None)
            else get_inner_type(inner)
        )
        self.size = size
        self.inner = inner if inner_type else getattr(inner, "inner", None)
        self.inner.store_in_ast(self.to_type())

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
        return VectorType(inner=None, inner_type=inner_type)

    @classmethod
    def init_as_template_type(cls, inner_type) -> "Vector[T]":
        return Vector(inner=None, inner_type=inner_type, size=None)


class TupleNew(Generic[T, U]):
    """Tuple new operation."""

    inner_type: NadaType
    inner: typing.Tuple[T, U]
    source_ref: SourceRef

    def __init__(
        self, inner_type: NadaType, inner: typing.Tuple[T, U], source_ref: SourceRef
    ):
        self.id = id(self)
        self.inner = inner
        self.source_ref = source_ref
        self.inner_type = inner_type

    def store_in_ast(self, ty: object):
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.inner.id for element in self.inner],
            source_ref=self.source_ref,
            ty=ty,
            inner_type=self.inner_type,
        )


def unzip(array: Array[Tuple[T, R]]) -> Tuple[Array[T], Array[R]]:
    right_type = ArrayType(inner_type=array.inner_type.right_type, size=array.size)
    left_type = ArrayType(inner_type=array.inner_type.left_type, size=array.size)

    return Tuple(
        right_type=right_type,
        left_type=left_type,
        inner=Unzip(inner=array, source_ref=SourceRef.back_frame()),
    )


@dataclass
class ArrayNew(Generic[T]):
    """Array new operation"""

    inner_type: NadaType
    inner: List[T]
    source_ref: SourceRef

    def __init__(self, inner_type: NadaType, inner: List[T], source_ref: SourceRef):
        self.id = id(self)
        self.inner = inner
        self.source_ref = source_ref
        self.inner_type = inner_type

    def store_in_ast(self, ty: NadaType):
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.inner.id for element in self.inner],
            source_ref=self.source_ref,
            ty=ty,
            inner_type=self.inner_type,
        )
