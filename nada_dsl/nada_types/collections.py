"""Nada Collection type definitions."""

from dataclasses import dataclass
from typing import Any, Dict, Generic, List
import typing

from sortedcontainers import SortedDict

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    MapASTOperation,
    TupleAccessorASTOperation,
    NTupleAccessorASTOperation,
    NewASTOperation,
    ObjectAccessorASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
)
from nada_dsl.nada_types import DslType

# Wildcard import due to non-zero types
from nada_dsl.nada_types.scalar_types import *  # pylint: disable=W0614:wildcard-import
from nada_dsl.source_ref import SourceRef
from nada_dsl.errors import (
    IncompatibleTypesError,
    InvalidTypeError,
    NotAllowedException,
)
from nada_dsl.nada_types.function import NadaFunction, create_nada_fn
from nada_dsl.nada_types.generics import U, T, R
from . import AllTypes, OperationType


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


@dataclass
class Map(Generic[T, R]):
    """The Map operation"""

    child: OperationType
    fn: NadaFunction[T, R]
    source_ref: SourceRef

    def __init__(
        self,
        child: OperationType,
        fn: NadaFunction[T, R],
        source_ref: SourceRef,
    ):
        self.id = OperationId.next()
        self.child = child
        self.fn = fn
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store MP in AST"""
        AST_OPERATIONS[self.id] = MapASTOperation(
            id=self.id,
            child=self.child.child.id,
            fn=self.fn.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class Reduce(Generic[T, R]):
    """The Nada Reduce operation."""

    child: OperationType
    fn: NadaFunction[T, R]
    initial: R
    source_ref: SourceRef

    def __init__(
        self,
        child: OperationType,
        fn: NadaFunction[T, R],
        initial: R,
        source_ref: SourceRef,
    ):
        self.id = OperationId.next()
        self.child = child
        self.fn = fn
        self.initial = initial
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store a reduce object in AST"""
        AST_OPERATIONS[self.id] = ReduceASTOperation(
            id=self.id,
            child=self.child.child.id,
            fn=self.fn.id,
            initial=self.initial.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class TupleType(NadaType):
    """Marker type for Tuples."""

    is_compound = True

    def __init__(self, left_type: NadaType, right_type: NadaType):
        self.left_type = left_type
        self.right_type = right_type

    def instantiate(self, child_or_value):
        return Tuple(child_or_value, self.left_type, self.right_type)

    def to_mir(self) -> proto_ty.NadaType:
        """Convert a tuple object into a Nada type."""
        return proto_ty.NadaType(
            tuple=proto_ty.Tuple(
                left=self.left_type.to_mir(), right=self.right_type.to_mir()
            )
        )


def _generate_accessor(ty: Any, accessor: Any) -> DslType:
    if hasattr(ty, "ty") and ty.ty.is_literal():  # TODO: fix
        raise TypeError("Literals are not supported in accessors")
    return ty.instantiate(accessor)


@dataclass
class Tuple(Generic[T, U], DslType):
    """The Tuple type"""

    left_type: NadaType
    right_type: NadaType

    def __init__(self, child, left_type: NadaType, right_type: NadaType):
        self.left_type = left_type
        self.right_type = right_type
        self.child = child
        super().__init__(self.child)

    @classmethod
    def new(cls, left_value: T, right_value: U) -> "Tuple[T, U]":
        """Constructs a new Tuple."""
        return Tuple(
            left_type=left_value.type(),
            right_type=right_value.type(),
            child=TupleNew(
                child=(left_value, right_value),
                source_ref=SourceRef.back_frame(),
            ),
        )

    @classmethod
    def generic_type(cls, left_type: U, right_type: T) -> TupleType:
        """Returns the generic type for this Tuple"""
        return TupleType(left_type=left_type, right_type=right_type)

    @property
    def left(self) -> DslType:
        """The left element of the  Tuple."""
        accessor = TupleAccessor(
            index=0,
            child=self,
            source_ref=SourceRef.back_frame(),
        )

        return _generate_accessor(self.left_type, accessor)

    @property
    def right(self) -> DslType:
        """The right element of the Tuple."""
        accessor = TupleAccessor(
            index=1,
            child=self,
            source_ref=SourceRef.back_frame(),
        )

        return _generate_accessor(self.right_type, accessor)

    def type(self):
        """Metatype for Tuple"""
        return TupleType(self.left_type, self.right_type)


@dataclass
class TupleAccessor:
    """Accessor for Tuple"""

    child: Tuple
    index: int
    source_ref: SourceRef

    def __init__(
        self,
        child: Tuple,
        index: int,
        source_ref: SourceRef,
    ):
        self.id = OperationId.next()
        self.child = child
        self.index = index
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this accessor in the AST."""
        AST_OPERATIONS[self.id] = TupleAccessorASTOperation(
            id=self.id,
            source=self.child.child.id,
            index=self.index,
            source_ref=self.source_ref,
            ty=ty,
        )


class NTupleType(NadaType):
    """Marker type for NTuples."""

    is_compound = True

    def __init__(self, types: List[NadaType]):
        self.types = types

    def instantiate(self, child_or_value):
        return NTuple(child_or_value, self.types)

    def to_mir(self) -> proto_ty.NadaType:
        """Convert a tuple object into a Nada type."""
        return proto_ty.NadaType(
            ntuple=proto_ty.Ntuple(fields=[ty.to_mir() for ty in self.types])
        )


@dataclass
class NTuple(DslType):
    """The NTuple type"""

    types: List[Any]

    def __init__(self, child, types: List[Any]):
        self.types = types
        self.child = child
        super().__init__(self.child)

    @classmethod
    def new(cls, values: List[Any]) -> "NTuple":
        """Constructs a new NTuple."""
        types = [value.type() for value in values]
        return NTuple(
            types=types,
            child=NTupleNew(
                child=values,
                source_ref=SourceRef.back_frame(),
            ),
        )

    def __getitem__(self, index: int) -> DslType:
        if index >= len(self.types):
            raise IndexError(f"Invalid index {index} for NTuple.")

        accessor = NTupleAccessor(
            index=index,
            child=self,
            source_ref=SourceRef.back_frame(),
        )

        return _generate_accessor(self.types[index], accessor)

    def type(self):
        """Metatype for NTuple"""
        return NTupleType(self.types)


@dataclass
class NTupleAccessor:
    """Accessor for NTuple"""

    child: NTuple
    index: int
    source_ref: SourceRef

    def __init__(
        self,
        child: NTuple,
        index: int,
        source_ref: SourceRef,
    ):
        self.id = OperationId.next()
        self.child = child
        self.index = index
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this accessor in the AST."""
        AST_OPERATIONS[self.id] = NTupleAccessorASTOperation(
            id=self.id,
            source=self.child.child.id,
            index=self.index,
            source_ref=self.source_ref,
            ty=ty,
        )


class ObjectType(NadaType):
    """Marker type for Objects."""

    is_compound = True

    def __init__(self, types: Dict[str, NadaType]):
        self.types = types

    def to_mir(self) -> proto_ty.NadaType:
        """Convert an object into a Nada type."""
        fields = SortedDict({name: ty.to_mir() for name, ty in self.types.items()})
        return proto_ty.NadaType(
            object=proto_ty.Object(
                fields=[
                    proto_ty.ObjectEntry(name=k, type=v) for k, v in fields.items()
                ],
            )
        )

    def instantiate(self, child_or_value):
        return Object(child_or_value, self.types)


@dataclass
class Object(DslType):
    """The Object type"""

    types: Dict[str, Any]

    def __init__(self, child, types: Dict[str, Any]):
        self.types = types
        self.child = child
        super().__init__(self.child)

    @classmethod
    def new(cls, values: Dict[str, Any]) -> "Object":
        """Constructs a new Object."""
        types = {key: value.type() for key, value in values.items()}
        return Object(
            types=types,
            child=ObjectNew(
                child=values,
                source_ref=SourceRef.back_frame(),
            ),
        )

    def __getattr__(self, attr: str) -> DslType:
        if attr not in self.types:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{attr}'"
            )

        accessor = ObjectAccessor(
            key=attr,
            child=self,
            source_ref=SourceRef.back_frame(),
        )

        return _generate_accessor(self.types[attr], accessor)

    def type(self):
        """Metatype for Object"""
        return ObjectType(types=self.types)


@dataclass
class ObjectAccessor:
    """Accessor for Object"""

    child: Object
    key: str
    source_ref: SourceRef

    def __init__(
        self,
        child: Object,
        key: str,
        source_ref: SourceRef,
    ):
        self.id = OperationId.next()
        self.child = child
        self.key = key
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this accessor in the AST."""
        AST_OPERATIONS[self.id] = ObjectAccessorASTOperation(
            id=self.id,
            source=self.child.child.id,
            key=self.key,
            source_ref=self.source_ref,
            ty=ty,
        )


class Zip:
    """The Zip operation."""

    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = OperationId.next()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store a Zip object in the AST."""
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            variant=proto_op.BinaryOperationVariant.ZIP,
            left=self.left.child.id,
            right=self.right.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Unzip:
    """The Unzip operation."""

    def __init__(self, child: AllTypes, source_ref: SourceRef):
        self.id = OperationId.next()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store an Unzip object in the AST."""
        AST_OPERATIONS[self.id] = UnaryASTOperation(
            id=self.id,
            variant=proto_op.UnaryOperationVariant.UNZIP,
            child=self.child.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class InnerProduct:
    """Inner product of two arrays."""

    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = OperationId.next()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store the InnerProduct object in the AST."""
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            variant=proto_op.BinaryOperationVariant.INNER_PRODUCT,
            left=self.left.child.id,
            right=self.right.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class ArrayType(NadaType):
    """Marker type for arrays."""

    is_compound = True

    def __init__(self, contained_type: NadaType, size: int):
        self.contained_type = contained_type
        self.size = size

    def to_mir(self) -> proto_ty.NadaType:
        """Convert this generic type into a MIR Nada type."""
        return proto_ty.NadaType(
            array=proto_ty.Array(
                size=self.size, contained_type=self.contained_type.to_mir()
            )
        )

    def instantiate(self, child_or_value):
        return Array(child_or_value, self.size, self.contained_type)


@dataclass
class Array(Generic[T], DslType):
    """Nada Array type.

    This is the representation of arrays in Nada MIR.
    Arrays have public, fixed size at compile time.

    Attributes
    ----------
    contained_type: T
        The type of the array
    child:
        The optional child operation
    size: int
        The size of the array
    """

    contained_type: NadaType
    size: int

    def __init__(self, child, size: int, contained_type: NadaType = None):
        self.contained_type = (
            contained_type if contained_type is not None else child.type()
        )

        self.size = size
        self.child = (
            child if contained_type is not None else getattr(child, "child", None)
        )
        if self.child is not None:
            self.child.store_in_ast(self.type().to_mir())

    def __iter__(self):
        raise NotAllowedException(
            "Cannot loop over a Nada Array, use functional style Array operations (map, reduce, zip)."
        )

    def check_not_constant(self, ty):
        """Checks that a type is not a constant"""
        if ty.is_constant:
            raise NotAllowedException(
                "functors (map and reduce) can't be called with constant args"
            )

    def map(self: "Array[T]", function) -> "Array":
        """The map operation for Arrays."""
        self.check_not_constant(self.contained_type)
        nada_function = create_nada_fn(function, args_ty=[self.contained_type])
        return Array(
            size=self.size,
            contained_type=nada_function.return_type,
            child=Map(child=self, fn=nada_function, source_ref=SourceRef.back_frame()),
        )

    def reduce(self: "Array[T]", function, initial: R) -> R:
        """The Reduce operation for arrays."""
        self.check_not_constant(self.contained_type)
        self.check_not_constant(initial.type())
        function = create_nada_fn(
            function, args_ty=[initial.type(), self.contained_type]
        )
        return function.return_type.instantiate(
            Reduce(
                child=self,
                fn=function,
                initial=initial,
                source_ref=SourceRef.back_frame(),
            )
        )

    def zip(self: "Array[T]", other: "Array[U]") -> "Array[Tuple[T, U]]":
        """The Zip operation for Arrays."""
        if self.size != other.size:
            raise IncompatibleTypesError("Cannot zip arrays of different size")
        return Array(
            size=self.size,
            contained_type=TupleType(
                left_type=self.contained_type,
                right_type=other.contained_type,
            ),
            child=Zip(left=self, right=other, source_ref=SourceRef.back_frame()),
        )

    def inner_product(self: "Array[T]", other: "Array[T]") -> T:
        """The child product operation for arrays"""
        if self.size != other.size:
            raise IncompatibleTypesError(
                "Cannot do child product of arrays of different size"
            )

        if is_primitive_integer(self.contained_type) and is_primitive_integer(
            other.contained_type
        ):
            return self.contained_type.instantiate(
                InnerProduct(left=self, right=other, source_ref=SourceRef.back_frame())
            )  # type: ignore

        raise InvalidTypeError(
            "Inner product is only implemented for arrays of integer types"
        )

    @classmethod
    def new(cls, *args) -> "Array[T]":
        """Constructs a new Array."""
        if len(args) == 0:
            raise ValueError("At least one value is required")

        first_arg = args[0]
        if not all(isinstance(arg, type(first_arg)) for arg in args):
            raise TypeError("All arguments must be of the same type")

        return Array(
            contained_type=first_arg.type(),
            size=len(args),
            child=ArrayNew(
                child=args,
                source_ref=SourceRef.back_frame(),
            ),
        )

    def type(self):
        """Metatype for Array"""
        return ArrayType(self.contained_type, self.size)


@dataclass
class TupleNew(Generic[T, U]):
    """MIR Tuple new operation.

    Represents the creation of a new Tuple.
    """

    child: typing.Tuple[T, U]
    source_ref: SourceRef

    def __init__(self, child: typing.Tuple[T, U], source_ref: SourceRef):
        self.id = OperationId.next()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this TupleNew in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.child.id for element in self.child],
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class NTupleNew:
    """MIR NTuple new operation.

    Represents the creation of a new Tuple.
    """

    child: List[DslType]
    source_ref: SourceRef

    def __init__(self, child: List[DslType], source_ref: SourceRef):
        self.id = OperationId.next()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this NTupleNew in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.child.id for element in self.child],
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class ObjectNew:
    """MIR Object new operation.

    Represents the creation of a new Object.
    """

    child: Dict[str, DslType]
    source_ref: SourceRef

    def __init__(self, child: Dict[str, DslType], source_ref: SourceRef):
        self.id = OperationId.next()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this Object in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.child.id for element in self.child.values()],
            source_ref=self.source_ref,
            ty=ty,
        )


def unzip(array: Array[Tuple[T, R]]) -> Tuple[Array[T], Array[R]]:
    """The Unzip operation for Arrays."""
    right_type = ArrayType(
        contained_type=array.contained_type.right_type, size=array.size
    )
    left_type = ArrayType(
        contained_type=array.contained_type.left_type, size=array.size
    )

    return Tuple(
        right_type=right_type,
        left_type=left_type,
        child=Unzip(child=array, source_ref=SourceRef.back_frame()),
    )


@dataclass
class ArrayNew(Generic[T]):
    """MIR Array new operation"""

    child: List[T]
    source_ref: SourceRef

    def __init__(self, child: List[T], source_ref: SourceRef):
        self.id = OperationId.next()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store this ArrayNew object in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.child.id for element in self.child],
            source_ref=self.source_ref,
            ty=ty,
        )
