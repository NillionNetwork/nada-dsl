"""Nada Collection type definitions."""

import copy
from dataclasses import dataclass
import inspect
import json
import traceback
from typing import Any, Generic, List, Optional
import typing
from typing import TypeVar

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    MapASTOperation,
    NewASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
    ASTOperation,
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
        if isinstance(self, (Vector, VectorType)):
            inner_type = self.retrieve_inner_type()
            return {"Vector": {"inner_type": inner_type}}
        if isinstance(self, (Tuple, TupleType)):
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
        raise InvalidTypeError(
            f"{self.__class__.__name__} is not a valid Nada Collection"
        )

    def retrieve_inner_type(self):
        """Retrieves the inner type of this collection"""
        if isinstance(self.inner_type, TypeVar):
            return "T"
        if inspect.isclass(self.inner_type):
            return self.inner_type.class_to_type()
        return self.inner_type.to_type()


class Map(Generic[T, R]):
    """The Map operation"""

    inner: OperationType
    fn: NadaFunction[T, R]
    source_ref: SourceRef

    def __init__(
        self,
        inner: OperationType,
        fn: NadaFunction[T, R],
        source_ref: SourceRef,
    ):
        self.id = next_operation_id()
        self.inner = inner
        self.fn = fn
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        """Store MP in AST"""
        AST_OPERATIONS[self.id] = MapASTOperation(
            id=self.id,
            inner=self.inner.inner.id,
            fn=self.fn.id,
            source_ref=self.source_ref,
            ty=ty,
        )


@dataclass
class Reduce(Generic[T, R]):
    """The Nada Reduce operation."""

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
        self.id = next_operation_id()
        self.inner = inner
        self.fn = fn
        self.initial = initial
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        """Store a reduce object in AST"""
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
        """Convert a tuple object into a Nada type."""
        return {
            "Tuple": {
                "left_type": self.left_type.to_type(),
                "right_type": self.right_type.to_type(),
            }
        }


class Tuple(Generic[T, U], Collection):
    """The Tuple type"""

    left_type: T
    right_type: U

    def __init__(self, inner, left_type: T, right_type: U):
        self.left_type = left_type
        self.right_type = right_type
        self.inner = inner
        super().__init__(self.inner)

    @classmethod
    def new(cls, left_type: T, right_type: U) -> "Tuple[T, U]":
        """Constructs a new Tuple."""
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
        """Returns the generic type for this Tuple"""
        return TupleType(left_type=left_type, right_type=right_type)

@dataclass
class ObjectProperty(NadaType):
    parent_object_id: int
    source_ref: SourceRef
    id: int

    def __init__(
        self,
        parent_object_id: int,
        source_ref: SourceRef,
    ):
        self.id = next_operation_id()
        self.parent_object_id = parent_object_id
        self.source_ref = source_ref
        self.store_in_ast(self)

    def store_in_ast(self, ty):
        """Store a reduce object in AST"""
        AST_OPERATIONS[self.id] = ObjectPropertyASTOperation(
            id=self.id,
            parent_object_id=self.parent_object_id,
            source_ref=self.source_ref,
            ty=ty,
        )

@dataclass
class ObjectPropertyASTOperation(ASTOperation):
    """AST Representation of a Reduce operation."""

    parent_object_id: int

    def inner_operations(self):
        return [self.parent_object_id]

    def to_mir(self):
        return {
            "ObjectProperty": {
                "id": self.id,
                "parent_object_id": self.parent_object_id,
                "type": self.ty,
                "source_ref_index": self.source_ref.to_index(),
            }
        }
    
def types_from_json(value: dict, is_public: bool):
    if not isinstance(value, dict):
        raise ValueError(
            "Expected root type of a document to be a dictionary"
        ) 

    result = {}
    for name, value in value.items():
        result[name] = _types_from_json(value, is_public)
    return result

def _types_from_json(value: Any, is_public: bool):
    result = {}
    if isinstance(value, bool):
        result = "SecretBoolean" if not is_public else "Boolean"
    elif isinstance(value, int):
        result = "SecretInteger" if not is_public else "Integer"
    elif isinstance(value, list):
        types = [_types_from_json(v, is_public) for v in value]
        
        # Check if all types in the list are the same
        unique_types = set(types)
        if len(unique_types) == 1:
            # Use "Array" instead of "NTuple" if all types are the same
            result = { "Array": { "inner_type": types[0], "size": len(types) } }
        else:
            result = { "NTuple": { "types": types } }
    elif isinstance(value, dict):
        types = {k: _types_from_json(v, is_public) for k, v in value.items()}
        result = { "Object": { "types": types } }
    return result

class TreeDict:
    def __init__(self, tree):
        self._tree = tree

    def __getattr__(self, item):
        return self.lookup(self._tree, item)

    @staticmethod
    def lookup(value, item):
        if item in value:
            result = value[item]
            if isinstance(result, dict):
                # Wrap the nested dictionary in another TreeDict
                return TreeDict(result)
            return result
        raise AttributeError(f"Item '{item}' not found")

class _Object(NadaType):
    tree_dict: TreeDict

    def __init__(self, inner: OperationType, source_file: str, is_public: bool) -> None:
        self.id = next_operation_id()
        self.inner = inner
        with open(source_file) as f:
            content = f.read()
        source = json.loads(content)
        self.tree_dict = types_from_json(source, is_public)
        self.store_in_ast(self)
        super().__init__(inner)

    def __getattr__(self, item):
        result = TreeDict.lookup(self.tree_dict, item)
        print(f"result = {result}")
        #scalar = new_scalar_type(Mode.PUBLIC, BaseType.INTEGER)(ObjectProperty(parent_object_id=self.id, source_ref=SourceRef.back_frame()))
        #return scalar # TODO
      
    def to_type(self):
        return {"Object": {"types": 
            self.tree_dict
        }}
    
    def store_in_ast(self, ty):
        """Store a reduce object in AST"""
        AST_OPERATIONS[self.id] = ObjectASTOperation(
            id=self.id,
            inner=self.inner.id,
            source_ref=SourceRef.back_frame(),
            ty=ty,
        )


@dataclass
class ObjectASTOperation(ASTOperation):
    """AST Representation of a Reduce operation."""

    inner: int

    def inner_operations(self):
        return [self.inner]

    def to_mir(self):
        return {
            "Object": {
                "id": self.id,
                "inner": self.inner,
                #"type": self.ty,
                "source_ref_index": 0, #TMP self.source_ref.to_index(),
            }
        }
    


class PublicDocument(_Object):
    def __init__(self, inner: OperationType,  source_file: str) -> None:
        super().__init__(inner, source_file, True)


class PrivateDocument(_Object):
    def __init__(self, inner: OperationType,  source_file: str) -> None:
        super().__init__(inner, source_file, False)


def get_inner_type(inner_type):
    """Utility that returns the inner type for a composite type."""
    inner_type = copy.copy(inner_type)
    setattr(inner_type, "inner", None)
    return inner_type


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
            left=self.left.inner.id,
            right=self.right.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Unzip:
    """The Unzip operation."""

    def __init__(self, inner: AllTypes, source_ref: SourceRef):
        self.id = next_operation_id()
        self.inner = inner
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        """Store an Unzip object in the AST."""
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
        self.id = next_operation_id()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: NadaTypeRepr):
        """Store the InnerProduct object in the AST."""
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
        """Convert this generic type into a MIR Nada type."""
        return {"Array": {"inner_type": self.inner_type.to_type(), "size": self.size}}


class Array(Generic[T], Collection):
    """Nada Array type.

    This is the representation of arrays in Nada MIR.
    Arrays have public, fixed size at compile time.

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
            inner_type=nada_function.return_type,
            inner=Map(inner=self, fn=nada_function, source_ref=SourceRef.back_frame()),
        )

    def reduce(self: "Array[T]", function, initial: R) -> R:
        """The Reduce operation for arrays."""
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
        """The Zip operation for Arrays."""
        if self.size != other.size:
            raise IncompatibleTypesError("Cannot zip arrays of different size")
        return Array(
            size=self.size,
            inner_type=Tuple(
                left_type=self.inner_type, right_type=other.inner_type, inner=None
            ),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame()),
        )

    def inner_product(self: "Array[T]", other: "Array[T]") -> T:
        """The inner product operation for arrays"""
        if self.size != other.size:
            raise IncompatibleTypesError(
                "Cannot do inner product of arrays of different size"
            )

        if is_primitive_integer(self.retrieve_inner_type()) and is_primitive_integer(
            other.retrieve_inner_type()
        ):
            inner_type = (
                self.inner_type
                if inspect.isclass(self.inner_type)
                else self.inner_type.__class__
            )
            return inner_type(
                inner=InnerProduct(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
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
        """Return the generic type of the Array."""
        return ArrayType(inner_type=inner_type, size=size)

    @classmethod
    def init_as_template_type(cls, inner_type) -> "Array[T]":
        """Construct an empty template array with the given inner type."""
        return Array(inner=None, inner_type=inner_type, size=None)


@dataclass
class VectorType(Collection):
    """The generic type for Vectors."""

    inner_type: AllTypesType


@dataclass
class Vector(Generic[T], Collection):
    """
    The Vector Nada Type.

    This is the representation of Vector types in Nada MIR.
    A Vector is similar to the Array type but the difference is that
    its size may change at runtime.
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
        raise NotAllowedException(
            "Cannot iterate/for loop over a nada Vector,"
            + " use functional style Vector functions instead (map, reduce, zip)"
        )

    def map(self: "Vector[T]", function: NadaFunction[T, R]) -> "Vector[R]":
        """The map operation for Nada Vectors."""
        return Vector(
            size=self.size,
            inner_type=function.return_type,
            inner=(Map(inner=self, fn=function, source_ref=SourceRef.back_frame())),
        )

    def zip(self: "Vector[T]", other: "Vector[R]") -> "Vector[Tuple[T, R]]":
        """The Zip operation for Nada Vectors."""
        return Vector(
            size=self.size,
            inner_type=Tuple.generic_type(self.inner_type, other.inner_type),
            inner=Zip(left=self, right=other, source_ref=SourceRef.back_frame()),
        )

    def reduce(
        self: "Vector[T]", function: NadaFunction[T, R], initial: Optional[R] = None
    ) -> R:
        """The reduce operation for Nada Vectors."""
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
        """Returns the generic type for a Vector with the given inner type."""
        return VectorType(inner=None, inner_type=inner_type)

    @classmethod
    def init_as_template_type(cls, inner_type) -> "Vector[T]":
        """Construct an empty Vector with the given inner type."""
        return Vector(inner=None, inner_type=inner_type, size=None)


class TupleNew(Generic[T, U]):
    """MIR Tuple new operation.

    Represents the creation of a new Tuple.
    """

    inner_type: NadaType
    inner: typing.Tuple[T, U]
    source_ref: SourceRef

    def __init__(
        self, inner_type: NadaType, inner: typing.Tuple[T, U], source_ref: SourceRef
    ):
        self.id = next_operation_id()
        self.inner = inner
        self.source_ref = source_ref
        self.inner_type = inner_type

    def store_in_ast(self, ty: object):
        """Store this TupleNew in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.inner.id for element in self.inner],
            source_ref=self.source_ref,
            ty=ty,
            inner_type=self.inner_type,
        )


def unzip(array: Array[Tuple[T, R]]) -> Tuple[Array[T], Array[R]]:
    """The Unzip operation for Arrays."""
    right_type = ArrayType(inner_type=array.inner_type.right_type, size=array.size)
    left_type = ArrayType(inner_type=array.inner_type.left_type, size=array.size)

    return Tuple(
        right_type=right_type,
        left_type=left_type,
        inner=Unzip(inner=array, source_ref=SourceRef.back_frame()),
    )


@dataclass
class ArrayNew(Generic[T]):
    """MIR Array new operation"""

    inner_type: NadaType
    inner: List[T]
    source_ref: SourceRef

    def __init__(self, inner_type: NadaType, inner: List[T], source_ref: SourceRef):
        self.id = next_operation_id()
        self.inner = inner
        self.source_ref = source_ref
        self.inner_type = inner_type

    def store_in_ast(self, ty: NadaType):
        """Store this ArrayNew object in the AST."""
        AST_OPERATIONS[self.id] = NewASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            elements=[element.inner.id for element in self.inner],
            source_ref=self.source_ref,
            ty=ty,
            inner_type=self.inner_type,
        )
