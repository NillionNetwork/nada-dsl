"""Nada Collection type definitions."""

import copy
from dataclasses import dataclass
import inspect
import traceback
from typing import Any, Dict, Generic, List
import typing
from typing import TypeVar

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    MapASTOperation,
    NTupleAccessorASTOperation,
    NewASTOperation,
    ObjectAccessorASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
)
from nada_dsl.nada_types import NadaType

# Wildcard import due to non-zero types
from nada_dsl.nada_types.scalar_types import *  # pylint: disable=W0614:wildcard-import
from nada_dsl.source_ref import SourceRef
from nada_dsl.errors import (
    IncompatibleTypesError,
    InvalidTypeError,
    NotAllowedException,
)
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
        self.id = next_operation_id()
        self.child = child
        self.fn = fn
        self.source_ref = source_ref

    def store_in_ast(self, ty):
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
        self.id = next_operation_id()
        self.child = child
        self.fn = fn
        self.initial = initial
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        """Store a reduce object in AST"""
        AST_OPERATIONS[self.id] = ReduceASTOperation(
            id=self.id,
            child=self.child.child.id,
            fn=self.fn.id,
            initial=self.initial.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class TupleMetaType(MetaType):
    """Marker type for Tuples."""

    left_type: NadaType
    right_type: NadaType

    def instantiate(self, child):
        return Tuple(child, self.left_type, self.right_type)

    def to_mir(self):
        """Convert a tuple object into a Nada type."""
        return {
            "Tuple": {
                "left_type": self.left_type.to_mir(),
                "right_type": self.right_type.to_mir(),
            }
        }


@dataclass
class Tuple(Generic[T, U], NadaType):
    """The Tuple type"""

    left_type: T
    right_type: U

    def __init__(self, child, left_type: T, right_type: U):
        self.left_type = left_type
        self.right_type = right_type
        self.child = child
        super().__init__(self.child)

    """TODO this should be deleted and use MetaType.to_mir"""

    # def to_mir(self):
    #     return {
    #         "Tuple": {
    #             "left_type": (
    #                 self.left_type.to_mir()
    #                 if isinstance(
    #                     self.left_type, (NadaType, ArrayMetaType, TupleMetaType)
    #                 )
    #                 else self.left_type.class_to_mir()
    #             ),
    #             "right_type": (
    #                 self.right_type.to_mir()
    #                 if isinstance(
    #                     self.right_type,
    #                     (NadaType, ArrayMetaType, TupleMetaType),
    #                 )
    #                 else self.right_type.class_to_mir()
    #             ),
    #         }
    #     }

    @classmethod
    def new(cls, left_value: NadaType, right_value: NadaType) -> "Tuple[T, U]":
        """Constructs a new Tuple."""
        return Tuple(
            left_type=left_value.metatype(),
            right_type=right_value.metatype(),
            child=TupleNew(
                child=(left_value, right_value),
                source_ref=SourceRef.back_frame(),
            ),
        )

    @classmethod
    def generic_type(cls, left_type: U, right_type: T) -> TupleMetaType:
        """Returns the generic type for this Tuple"""
        return TupleMetaType(left_type=left_type, right_type=right_type)

    def metatype(self):
        return TupleMetaType(self.left_type, self.right_type)


def _generate_accessor(ty: Any, accessor: Any) -> NadaType:
    if hasattr(ty, "ty") and ty.ty.is_literal():  # TODO: fix
        raise TypeError("Literals are not supported in accessors")
    return ty.instantiate(accessor)
    # if ty.is_scalar():
    #     if ty.is_literal():
    #         return ty  # value.instantiate(child=accessor) ?
    #     return ty(child=accessor)
    # if ty == Array:
    #     return Array(
    #         child=accessor,
    #         contained_type=ty.contained_type,
    #         size=ty.size,
    #     )
    # if ty == NTuple:
    #     return NTuple(
    #         child=accessor,
    #         types=ty.types,
    #     )
    # if ty == Object:
    #     return Object(
    #         child=accessor,
    #         types=ty.types,
    #     )
    # raise TypeError(f"Unsupported type for accessor: {ty}")


@dataclass
class NTupleMetaType(MetaType):
    """Marker type for NTuples."""

    types: List[NadaType]

    def instantiate(self, child):
        return NTuple(child, self.types)

    def to_mir(self):
        """Convert a tuple object into a Nada type."""
        return {
            "NTuple": {
                "types": [ty.to_mir() for ty in self.types],
            }
        }


@dataclass
class NTuple(NadaType):
    """The NTuple type"""

    types: List[Any]

    def __init__(self, child, types: List[Any]):
        self.types = types
        self.child = child
        super().__init__(self.child)

    @classmethod
    def new(cls, values: List[Any]) -> "NTuple":
        """Constructs a new NTuple."""
        types = [value.metatype() for value in values]
        return NTuple(
            types=types,
            child=NTupleNew(
                child=values,
                source_ref=SourceRef.back_frame(),
            ),
        )

    def __getitem__(self, index: int) -> NadaType:
        if index >= len(self.types):
            raise IndexError(f"Invalid index {index} for NTuple.")

        accessor = NTupleAccessor(
            index=index,
            child=self,
            source_ref=SourceRef.back_frame(),
        )

        return _generate_accessor(self.types[index], accessor)

    """TODO this should be deleted and use MetaType.to_mir"""

    # def to_mir(self):
    #     return {
    #         "NTuple": {
    #             "types": [
    #                 (
    #                     ty.to_mir()
    #                     if isinstance(ty, (NadaType, ArrayMetaType, TupleMetaType))
    #                     else ty.class_to_mir()
    #                 )
    #                 for ty in self.types
    #             ]
    #         }
    #     }

    def metatype(self):
        return NTupleMetaType(self.types)


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
        self.id = next_operation_id()
        self.child = child
        self.index = index
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        """Store this accessor in the AST."""
        AST_OPERATIONS[self.id] = NTupleAccessorASTOperation(
            id=self.id,
            source=self.child.child.id,
            index=self.index,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class ObjectMetaType(MetaType):
    """Marker type for Objects."""

    types: Dict[str, Any]

    def to_mir(self):
        """Convert an object into a Nada type."""
        return {"Object": {name: ty.to_mir() for name, ty in self.types.items()}}

    def instantiate(self, child):
        return Object(child, self.types)


@dataclass
class Object(NadaType):
    """The Object type"""

    types: Dict[str, Any]

    def __init__(self, child, types: Dict[str, Any]):
        self.types = types
        self.child = child
        super().__init__(self.child)

    @classmethod
    def new(cls, values: Dict[str, Any]) -> "Object":
        """Constructs a new Object."""
        types = {key: value.metatype() for key, value in values.items()}
        return Object(
            types=types,
            child=ObjectNew(
                child=types,
                source_ref=SourceRef.back_frame(),
            ),
        )

    def __getattr__(self, attr: str) -> NadaType:
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

    """TODO delete this use Meta.to_mir"""

    # def to_mir(self):
    #     return {
    #         "Object": {
    #             "types": {
    #                 name: (
    #                     ty.to_mir()
    #                     if isinstance(ty, (NadaType, ArrayMetaType, TupleMetaType))
    #                     else ty.class_to_mir()
    #                 )
    #                 for name, ty in self.types.items()
    #             }
    #         }
    #     }

    def metatype(self):
        return ObjectMetaType(types=self.types)


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
        self.id = next_operation_id()
        self.child = child
        self.key = key
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
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
        self.id = next_operation_id()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        """Store a Zip object in the AST."""
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            name="Zip",
            left=self.left.child.id,
            right=self.right.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Unzip:
    """The Unzip operation."""

    def __init__(self, child: AllTypes, source_ref: SourceRef):
        self.id = next_operation_id()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        """Store an Unzip object in the AST."""
        AST_OPERATIONS[self.id] = UnaryASTOperation(
            id=self.id,
            name="Unzip",
            child=self.child.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class InnerProduct:
    """Inner product of two arrays."""

    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = next_operation_id()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        """Store the InnerProduct object in the AST."""
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            name="InnerProduct",
            left=self.left.child.id,
            right=self.right.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class ArrayMetaType(MetaType):
    """Marker type for arrays."""

    contained_type: AllTypesType
    size: int

    def to_mir(self):
        """Convert this generic type into a MIR Nada type."""
        size = {"size": self.size} if self.size else {}
        return {
            "Array": {"inner_type": self.contained_type.to_mir(), **size}  # TODO: why?
        }

    def instantiate(self, child):
        return Array(child, self.size, self.contained_type)


@dataclass
class Array(Generic[T], NadaType):
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

    contained_type: T
    size: int

    def __init__(self, child, size: int, contained_type: T = None):
        self.contained_type = (
            contained_type if (child is None or contained_type is not None) else child
        )

        # TODO: can we simplify the following 10 lines?
        # If it's not a metatype, fetch it
        if self.contained_type is not None and not isinstance(
            self.contained_type, MetaType
        ):
            self.contained_type = self.contained_type.metatype()

        self.size = size
        self.child = (
            child if contained_type is not None else getattr(child, "child", None)
        )
        if self.child is not None:
            self.child.store_in_ast(self.metatype().to_mir())

    def __iter__(self):
        raise NotAllowedException(
            "Cannot loop over a Nada Array, use functional style Array operations (map, reduce, zip)."
        )

    def map(self: "Array[T]", function) -> "Array":
        """The map operation for Arrays."""
        nada_function = function
        if not isinstance(function, NadaFunction):
            nada_function = nada_fn(function)
        return Array(
            size=self.size,
            contained_type=nada_function.return_type,
            child=Map(child=self, fn=nada_function, source_ref=SourceRef.back_frame()),
        )

    def reduce(self: "Array[T]", function, initial: R) -> R:
        """The Reduce operation for arrays."""
        if not isinstance(function, NadaFunction):
            function = nada_fn(function)
        return function.return_type(
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
            contained_type=TupleMetaType(
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
                child=InnerProduct(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )  # type: ignore

        raise InvalidTypeError(
            "Inner product is only implemented for arrays of integer types"
        )

    # TODO delete

    # def to_mir(self):
    #     size = {"size": self.size} if self.size else {}
    #     return {"Array": {"inner_type": self.contained_type, **size}}

    @classmethod
    def new(cls, *args) -> "Array[T]":
        """Constructs a new Array."""
        if len(args) == 0:
            raise ValueError("At least one value is required")

        first_arg = args[0]
        if not all(isinstance(arg, type(first_arg)) for arg in args):
            raise TypeError("All arguments must be of the same type")

        return Array(
            contained_type=first_arg,
            size=len(args),
            child=ArrayNew(
                child=args,
                source_ref=SourceRef.back_frame(),
            ),
        )

    @classmethod
    def init_as_template_type(cls, contained_type) -> "Array[T]":
        """Construct an empty template array with the given child type."""
        return Array(child=None, contained_type=contained_type, size=None)

    def metatype(self):
        return ArrayMetaType(self.contained_type, self.size)


@dataclass
class TupleNew(Generic[T, U]):
    """MIR Tuple new operation.

    Represents the creation of a new Tuple.
    """

    child: typing.Tuple[T, U]
    source_ref: SourceRef

    def __init__(self, child: typing.Tuple[T, U], source_ref: SourceRef):
        self.id = next_operation_id()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
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

    child: List[NadaType]
    source_ref: SourceRef

    def __init__(self, child: List[NadaType], source_ref: SourceRef):
        self.id = next_operation_id()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
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

    child: Dict[str, NadaType]
    source_ref: SourceRef

    def __init__(self, child: Dict[str, NadaType], source_ref: SourceRef):
        self.id = next_operation_id()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
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
    right_type = ArrayMetaType(
        contained_type=array.contained_type.right_type, size=array.size
    )
    left_type = ArrayMetaType(
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
        self.id = next_operation_id()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaType):
        """Store this ArrayNew object in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.child.id for element in self.child],
            source_ref=self.source_ref,
            ty=ty,
        )
