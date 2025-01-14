# pylint:disable=W0401,W0614
"""The Nada Scalar type definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, TypeVar
from typing_extensions import Self
from betterproto.lib.google.protobuf import Empty

from nada_mir_proto.nillion.nada.types import v1 as proto_ty

from nada_dsl.operations import *
from nada_dsl.program_io import Literal
from nada_dsl import SourceRef
from . import DslType, Mode, BaseType, OperationType


# Constant dictionary that stores all the Nada types and is use to
# convert from the (mode, base_type) representation to the concrete Nada type
# (Integer, SecretBoolean,...)

# pylint: disable=invalid-name
_AnyScalarType = TypeVar(
    "_AnyScalarType",
    "Integer",
    "UnsignedInteger",
    "Boolean",
    "PublicInteger",
    "PublicUnsignedInteger",
    "PublicBoolean",
    "SecretInteger",
    "SecretUnsignedInteger",
    "SecretBoolean",
)
# pylint: enable=invalid-name

AnyScalarType = Union[
    "Integer",
    "UnsignedInteger",
    "Boolean",
    "PublicInteger",
    "PublicUnsignedInteger",
    "PublicBoolean",
    "SecretInteger",
    "SecretUnsignedInteger",
    "SecretBoolean",
]

# pylint: disable=global-variable-not-assigned
SCALAR_TYPES: dict[tuple[Mode, BaseType], type[AnyScalarType]] = {}

AnyBoolean = Union["Boolean", "PublicBoolean", "SecretBoolean"]


class ScalarDslType(DslType):
    """The Nada Scalar type.
    This is the super class for all scalar types in Nada.
    These are:
        - Boolean, PublicBoolean, SecretBoolean
        - Integer, PublicInteger, SecretInteger
        - UnsignedInteger, PublicUnsignedInteger, SecretUnsignedInteger
    `ScalarType` provides common operation implementations for all the scalar types
    based on the typing rules of the Nada model.
    """

    def __init__(self, child: OperationType, base_type: BaseType, mode: Mode):
        super().__init__(child=child)
        self.base_type = base_type
        self.mode = mode

    def __eq__(self, other) -> AnyBoolean:  # type: ignore
        return equals_operation(
            "Equals", "==", self, other, lambda lhs, rhs: lhs == rhs
        )

    def __ne__(self, other) -> AnyBoolean:  # type: ignore
        return equals_operation(
            "NotEquals", "!=", self, other, lambda lhs, rhs: lhs != rhs
        )

    def to_public(self) -> Self:
        """Convert this scalar type into a public variable."""
        return self

    @classmethod
    def is_scalar(cls) -> bool:
        return True


def equals_operation(
    operation, operator, left: ScalarDslType, right: ScalarDslType, f
) -> AnyBoolean:
    """This function is an abstraction for the equality operations"""
    base_type = left.base_type
    if base_type != right.base_type:
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right.mode.value]))
    match mode:
        case Mode.CONSTANT:
            return Boolean(value=bool(f(left.value, right.value)))
        case Mode.PUBLIC:
            operation = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
            )
            return PublicBoolean(child=operation)
        case Mode.SECRET:
            operation = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
            )
            return SecretBoolean(child=operation)


def register_scalar_type(mode: Mode, base_type: BaseType):
    """Decorator used to register a new scalar type in the `SCALAR_TYPES` dictionary."""

    def decorator(scalar_type: type[_AnyScalarType]) -> type[_AnyScalarType]:
        SCALAR_TYPES[(mode, base_type)] = scalar_type
        scalar_type.mode = mode
        scalar_type.base_type = base_type
        return scalar_type

    return decorator


def new_scalar_type(mode: Mode, base_type: BaseType) -> type[AnyScalarType]:
    """Returns the corresponding MIR Nada Type"""
    global SCALAR_TYPES
    return SCALAR_TYPES[(mode, base_type)]


class NumericDslType(ScalarDslType):
    """The superclass of all the numeric types in Nada:
    - Integer, PublicInteger, SecretInteger
    - UnsignedInteger, PublicUnsignedInteger, SecretUnsignedInteger
    It provides common operation implementations for all the numeric types based
    on the typing rules of the Nada model.
    """

    value: int

    def __add__(self, other):
        return binary_arithmetic_operation(
            "Addition", "+", self, other, lambda lhs, rhs: lhs + rhs
        )

    def __sub__(self, other):
        return binary_arithmetic_operation(
            "Subtraction", "-", self, other, lambda lhs, rhs: lhs - rhs
        )

    def __mul__(self, other):
        return binary_arithmetic_operation(
            "Multiplication", "*", self, other, lambda lhs, rhs: lhs * rhs
        )

    def __truediv__(self, other):
        return binary_arithmetic_operation(
            "Division", "/", self, other, lambda lhs, rhs: lhs / rhs
        )

    def __mod__(self, other):
        return binary_arithmetic_operation(
            "Modulo", "%", self, other, lambda lhs, rhs: lhs % rhs
        )

    def __pow__(self, other):
        base_type = self.base_type
        if base_type != other.base_type or not (
            base_type in (BaseType.INTEGER, BaseType.UNSIGNED_INTEGER)
        ):
            raise TypeError(f"Invalid operation: {self} ** {other}")
        mode = Mode(max([self.mode.value, other.mode.value]))
        if mode == Mode.CONSTANT:
            return new_scalar_type(mode, base_type)(self.value**other.value)
        if mode == Mode.PUBLIC:
            child = Power(left=self, right=other, source_ref=SourceRef.back_frame())
            return new_scalar_type(mode, base_type)(child)
        raise TypeError(f"Invalid operation: {self} ** {other}")

    def __lshift__(self, other):
        return shift_operation(
            "LeftShift", "<<", self, other, lambda lhs, rhs: lhs << rhs
        )

    def __rshift__(self, other):
        return shift_operation(
            "RightShift", ">>", self, other, lambda lhs, rhs: lhs >> rhs
        )

    def __lt__(self, other) -> AnyBoolean:
        return binary_relational_operation(
            "LessThan", "<", self, other, lambda lhs, rhs: lhs < rhs
        )

    def __gt__(self, other) -> AnyBoolean:
        return binary_relational_operation(
            "GreaterThan", ">", self, other, lambda lhs, rhs: lhs > rhs
        )

    def __le__(self, other) -> AnyBoolean:
        return binary_relational_operation(
            "LessOrEqualThan", "<=", self, other, lambda lhs, rhs: lhs <= rhs
        )

    def __ge__(self, other) -> AnyBoolean:
        return binary_relational_operation(
            "GreaterOrEqualThan", ">=", self, other, lambda lhs, rhs: lhs >= rhs
        )

    def __radd__(self, other):
        """This adds support for builtin `sum` operation for numeric types."""
        if isinstance(other, int):
            other_type = new_scalar_type(mode=Mode.CONSTANT, base_type=self.base_type)(
                other
            )
            return self.__add__(other_type)

        return self.__add__(other)


def binary_arithmetic_operation(
    operation, operator, left: ScalarDslType, right: ScalarDslType, f
) -> ScalarDslType:
    """This function is an abstraction for the binary arithmetic operations.

    Arithmetic operations apply to Numeric types only in Nada."""
    base_type = left.base_type
    if base_type != right.base_type or not base_type.is_numeric():
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right.mode.value]))
    match mode:
        case Mode.CONSTANT:
            return new_scalar_type(mode, base_type)(f(left.value, right.value))
        case Mode.PUBLIC | Mode.SECRET:
            child = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
            )
            return new_scalar_type(mode, base_type)(child)


def shift_operation(
    operation, operator, left: ScalarDslType, right: ScalarDslType, f
) -> ScalarDslType:
    """This function is an abstraction for the shift operations"""
    base_type = left.base_type
    right_base_type = right.base_type
    if not base_type.is_numeric() or not right_base_type == BaseType.UNSIGNED_INTEGER:
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    right_mode = right.mode
    if right_mode == Mode.SECRET:
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right_mode.value]))
    match mode:
        case Mode.CONSTANT:
            return new_scalar_type(mode, base_type)(f(left.value, right.value))
        case Mode.PUBLIC | Mode.SECRET:
            child = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
            )
            return new_scalar_type(mode, base_type)(child)


def binary_relational_operation(
    operation, operator, left: ScalarDslType, right: ScalarDslType, f
) -> AnyBoolean:
    """This function is an abstraction for the binary relational operations"""
    base_type = left.base_type
    if base_type != right.base_type or not base_type.is_numeric():
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right.mode.value]))
    match mode:
        case Mode.CONSTANT:
            return new_scalar_type(mode, BaseType.BOOLEAN)(f(left.value, right.value))  # type: ignore
        case Mode.PUBLIC | Mode.SECRET:
            child = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
            )
            return new_scalar_type(mode, BaseType.BOOLEAN)(child)  # type: ignore


def public_equals_operation(
    left: ScalarDslType, right: ScalarDslType
) -> "PublicBoolean":
    """This function is an abstraction for the public_equals operation for all types."""
    base_type = left.base_type
    if base_type != right.base_type:
        raise TypeError(f"Invalid operation: {left}.public_equals({right})")
    if Mode.CONSTANT in (left.mode, right.mode):
        raise TypeError(f"Invalid operation: {left}.public_equals({right})")

    return PublicBoolean(
        child=PublicOutputEquality(
            left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
        )  # type: ignore
    )


class BooleanDslType(ScalarDslType):
    """This abstraction represents all boolean types:
    - Boolean, PublicBoolean, SecretBoolean
    It provides common operation implementations for all the boolean types, defined above.
    """

    def __and__(self, other):
        return binary_logical_operation(
            "BooleanAnd", "&", self, other, lambda lhs, rhs: lhs & rhs
        )

    def __or__(self, other):
        return binary_logical_operation(
            "BooleanOr", "|", self, other, lambda lhs, rhs: lhs | rhs
        )

    def __xor__(self, other):
        return binary_logical_operation(
            "BooleanXor", "^", self, other, lambda lhs, rhs: lhs ^ rhs
        )

    def if_else(self, arg_0: _AnyScalarType, arg_1: _AnyScalarType) -> _AnyScalarType:
        """This function implements the function 'if_else' for every class that extends 'BooleanType'."""
        base_type = arg_0.base_type
        if (
            base_type != arg_1.base_type
            or base_type == BaseType.BOOLEAN
            or self.mode == Mode.CONSTANT
        ):
            raise TypeError(f"Invalid operation: {self}.IfElse({arg_0}, {arg_1})")
        mode = Mode(max([self.mode.value, arg_0.mode.value, arg_1.mode.value]))
        child = IfElse(
            this=self, arg_0=arg_0, arg_1=arg_1, source_ref=SourceRef.back_frame()
        )
        if mode == Mode.CONSTANT:
            mode = Mode.PUBLIC
        return new_scalar_type(mode, base_type)(child)


def binary_logical_operation(
    operation, operator, left: ScalarDslType, right: ScalarDslType, f
) -> ScalarDslType:
    """This function is an abstraction for the logical operations."""
    base_type = left.base_type
    if base_type != right.base_type or not base_type == BaseType.BOOLEAN:
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right.mode.value]))
    if mode == Mode.CONSTANT:
        return Boolean(value=bool(f(left.value, right.value)))
    if mode == Mode.PUBLIC:
        operation = globals()[operation](
            left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
        )
        return PublicBoolean(child=operation)

    operation = globals()[operation](
        left=left, right=right, source_ref=SourceRef.back_frame().back_frame()
    )
    return SecretBoolean(child=operation)


class NadaType(ABC):
    """Abstract meta type"""

    is_constant = False
    is_scalar = False
    is_compound = False

    @abstractmethod
    def instantiate(self, child_or_value):
        """Creates a value corresponding to this meta type"""

    @abstractmethod
    def to_mir(self) -> proto_ty.NadaType:
        """Returns a MIR representation of this meta type"""


class TypePassthroughMixin(NadaType):
    """Mixin for meta types"""

    def instantiate(self, child_or_value):
        """Creates a value corresponding to this meta type"""
        return self.ty(child_or_value)

    def to_mir(self) -> proto_ty.NadaType:
        return proto_ty.NadaType(**{self.proto_ty: Empty()})


@register_scalar_type(Mode.CONSTANT, BaseType.INTEGER)
class Integer(NumericDslType):
    """The Nada Integer type.

    Represents a constant (literal) integer."""

    def __init__(self, value):
        value = int(value)
        super().__init__(
            Literal(value=value, source_ref=SourceRef.back_frame()),
            BaseType.INTEGER,
            Mode.CONSTANT,
        )
        self.value = value

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    @classmethod
    def is_literal(cls) -> bool:
        return True

    def type(self):
        return IntegerType()


class IntegerType(TypePassthroughMixin):
    """Meta type for integers"""

    ty = Integer
    is_constant = True
    is_scalar = True
    proto_ty = "integer"


@dataclass
@register_scalar_type(Mode.CONSTANT, BaseType.UNSIGNED_INTEGER)
class UnsignedInteger(NumericDslType):
    """The Nada Unsigned Integer type.

    Represents a constant (literal) unsigned integer."""

    value: int

    def __init__(self, value):
        value = int(value)
        super().__init__(
            Literal(value=value, source_ref=SourceRef.back_frame()),
            BaseType.UNSIGNED_INTEGER,
            Mode.CONSTANT,
        )
        self.value = value

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    @classmethod
    def is_literal(cls) -> bool:
        return True

    def type(self):
        return UnsignedIntegerType()


class UnsignedIntegerType(TypePassthroughMixin):
    """Meta type for unsigned integers"""

    ty = UnsignedInteger
    is_constant = True
    is_scalar = True
    proto_ty = "unsigned_integer"


@register_scalar_type(Mode.CONSTANT, BaseType.BOOLEAN)
class Boolean(BooleanDslType):
    """The Nada Boolean type.

    Represents a constant (literal) boolean."""

    value: bool

    def __init__(self, value):
        value = bool(value)
        super().__init__(
            Literal(value=value, source_ref=SourceRef.back_frame()),
            BaseType.BOOLEAN,
            Mode.CONSTANT,
        )
        self.value = value

    def __bool__(self) -> bool:
        return self.value

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def __invert__(self: "Boolean") -> "Boolean":
        return Boolean(value=bool(not self.value))

    @classmethod
    def is_literal(cls) -> bool:
        return True

    def type(self):
        return BooleanType()


class BooleanType(TypePassthroughMixin):
    """Meta type for booleans"""

    ty = Boolean
    is_constant = True
    is_scalar = True
    proto_ty = "boolean"


@register_scalar_type(Mode.PUBLIC, BaseType.INTEGER)
class PublicInteger(NumericDslType):
    """The Nada Public Unsigned Integer type.

    Represents a public unsigned integer in a program. This is a public variable
    evaluated at runtime."""

    def __init__(self, child: DslType):
        super().__init__(child, BaseType.INTEGER, Mode.PUBLIC)

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def public_equals(
        self, other: Union["PublicInteger", "SecretInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for Public integer types."""
        return public_equals_operation(self, other)

    def type(self):
        return PublicIntegerType()


class PublicIntegerType(TypePassthroughMixin):
    """Meta type for public integers"""

    ty = PublicInteger
    is_scalar = True
    proto_ty = "integer"


@register_scalar_type(Mode.PUBLIC, BaseType.UNSIGNED_INTEGER)
class PublicUnsignedInteger(NumericDslType):
    """The Nada Public Integer type.

    Represents a public integer in a program. This is a public variable
    evaluated at runtime."""

    def __init__(self, child: DslType):
        super().__init__(child, BaseType.UNSIGNED_INTEGER, Mode.PUBLIC)

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def public_equals(
        self, other: Union["PublicUnsignedInteger", "SecretUnsignedInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for Public unsigned integer types."""
        return public_equals_operation(self, other)

    def type(self):
        return PublicUnsignedIntegerType()


class PublicUnsignedIntegerType(TypePassthroughMixin):
    """Meta type for public unsigned integers"""

    ty = PublicUnsignedInteger
    is_scalar = True
    proto_ty = "unsigned_integer"


@dataclass
@register_scalar_type(Mode.PUBLIC, BaseType.BOOLEAN)
class PublicBoolean(BooleanDslType):
    """The Nada Public Boolean type.

    Represents a public boolean in a program. This is a public variable
    evaluated at runtime."""

    def __init__(self, child: DslType):
        super().__init__(child, BaseType.BOOLEAN, Mode.PUBLIC)

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def __invert__(self: "PublicBoolean") -> "PublicBoolean":
        operation = Not(this=self, source_ref=SourceRef.back_frame())
        return PublicBoolean(child=operation)

    def public_equals(
        self, other: Union["PublicUnsignedInteger", "SecretUnsignedInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for Public boolean types."""
        return public_equals_operation(self, other)

    def type(self):
        return PublicBooleanType()


class PublicBooleanType(TypePassthroughMixin):
    """Meta type for public booleans"""

    ty = PublicBoolean
    is_scalar = True
    proto_ty = "boolean"


@dataclass
@register_scalar_type(Mode.SECRET, BaseType.INTEGER)
class SecretInteger(NumericDslType):
    """The Nada secret integer type."""

    def __init__(self, child: DslType):
        super().__init__(child, BaseType.INTEGER, Mode.SECRET)

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def public_equals(
        self, other: Union["PublicInteger", "SecretInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for secret integer types."""
        return public_equals_operation(self, other)

    def trunc_pr(
        self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]
    ) -> "SecretInteger":
        """Probabilistic truncation for secret integers."""
        if isinstance(other, UnsignedInteger):
            operation = TruncPr(
                left=self, right=other, source_ref=SourceRef.back_frame()
            )
            return SecretInteger(child=operation)
        if isinstance(other, PublicUnsignedInteger):
            operation = TruncPr(
                left=self, right=other, source_ref=SourceRef.back_frame()
            )
            return SecretInteger(child=operation)

        raise TypeError(f"Invalid operation: {self}.trunc_pr({other})")

    @classmethod
    def random(cls) -> "SecretInteger":
        """Random operation for Secret integers."""
        return SecretInteger(child=Random(source_ref=SourceRef.back_frame()))

    def to_public(self: "SecretInteger") -> "PublicInteger":
        """Convert this secret integer into a public variable."""
        operation = Reveal(this=self, source_ref=SourceRef.back_frame())
        return PublicInteger(child=operation)

    def type(self):
        return SecretIntegerType()


class SecretIntegerType(TypePassthroughMixin):
    """Meta type for secret integers"""

    ty = SecretInteger
    is_scalar = True
    proto_ty = "secret_integer"


@dataclass
@register_scalar_type(Mode.SECRET, BaseType.UNSIGNED_INTEGER)
class SecretUnsignedInteger(NumericDslType):
    """The Nada Secret Unsigned integer type."""

    def __init__(self, child: DslType):
        super().__init__(child, BaseType.UNSIGNED_INTEGER, Mode.SECRET)

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def public_equals(
        self, other: Union["PublicUnsignedInteger", "SecretUnsignedInteger"]
    ) -> "PublicBoolean":
        """The public equality operation."""
        return public_equals_operation(self, other)

    def trunc_pr(
        self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]
    ) -> "SecretUnsignedInteger":
        """Probabilistic truncation operation."""
        if isinstance(other, UnsignedInteger):
            operation = TruncPr(
                left=self, right=other, source_ref=SourceRef.back_frame()
            )
            return SecretUnsignedInteger(child=operation)
        if isinstance(other, PublicUnsignedInteger):
            operation = TruncPr(
                left=self, right=other, source_ref=SourceRef.back_frame()
            )
            return SecretUnsignedInteger(child=operation)

        raise TypeError(f"Invalid operation: {self}.trunc_pr({other})")

    @classmethod
    def random(cls) -> "SecretUnsignedInteger":
        """Generate a random secret unsigned integer."""
        return SecretUnsignedInteger(child=Random(source_ref=SourceRef.back_frame()))

    def to_public(
        self: "SecretUnsignedInteger",
    ) -> "PublicUnsignedInteger":
        """Convert this secret into a public variable."""
        operation = Reveal(this=self, source_ref=SourceRef.back_frame())
        return PublicUnsignedInteger(child=operation)

    def type(self):
        return SecretUnsignedIntegerType()


class SecretUnsignedIntegerType(TypePassthroughMixin):
    """Meta type for secret unsigned integers"""

    ty = SecretUnsignedInteger
    is_scalar = True
    proto_ty = "secret_unsigned_integer"


@dataclass
@register_scalar_type(Mode.SECRET, BaseType.BOOLEAN)
class SecretBoolean(BooleanDslType):
    """The SecretBoolean Nada MIR type."""

    def __init__(self, child: DslType):
        super().__init__(child, BaseType.BOOLEAN, Mode.SECRET)

    def __eq__(self, other) -> AnyBoolean:
        return ScalarDslType.__eq__(self, other)

    def __invert__(self: "SecretBoolean") -> "SecretBoolean":
        operation = Not(this=self, source_ref=SourceRef.back_frame())
        return SecretBoolean(child=operation)

    def to_public(self: "SecretBoolean") -> "PublicBoolean":
        """Convert this secret into a public variable."""
        operation = Reveal(this=self, source_ref=SourceRef.back_frame())
        return PublicBoolean(child=operation)

    @classmethod
    def random(cls) -> "SecretBoolean":
        """Generate a random secret boolean."""
        return SecretBoolean(child=Random(source_ref=SourceRef.back_frame()))

    def type(self):
        return SecretBooleanType()


class SecretBooleanType(TypePassthroughMixin):
    """Meta type for secret booleans"""

    ty = SecretBoolean
    is_scalar = True
    proto_ty = "secret_boolean"


@dataclass
class EcdsaSignature(DslType):
    """The EcdsaSignature Nada MIR type."""

    def __init__(self, child: OperationType):
        super().__init__(child=child)

    def type(self):
        return EcdsaSignatureType()


class EcdsaSignatureType(TypePassthroughMixin):
    """Meta type for EcdsaSignatures"""

    ty = EcdsaSignature
    proto_ty = "ecdsa_signature"


@dataclass
class EcdsaDigestMessage(DslType):
    """The EcdsaDigestMessage Nada MIR type."""

    def __init__(self, child: OperationType):
        super().__init__(child=child)

    def type(self):
        return EcdsaDigestMessageType()


class EcdsaDigestMessageType(TypePassthroughMixin):
    """Meta type for EcdsaDigestMessages"""

    ty = EcdsaDigestMessage
    proto_ty = "ecdsa_digest_message"


@dataclass
class EcdsaPrivateKey(DslType):
    """The EcdsaPrivateKey Nada MIR type."""

    def __init__(self, child: OperationType):
        super().__init__(child=child)

    def ecdsa_sign(self, digest: "EcdsaDigestMessage") -> "EcdsaSignature":
        """Random operation for Secret integers."""
        return EcdsaSignature(
            child=EcdsaSign(left=self, right=digest, source_ref=SourceRef.back_frame())
        )

    def type(self):
        return EcdsaPrivateKeyType()


class EcdsaPrivateKeyType(TypePassthroughMixin):
    """Meta type for EcdsaPrivateKeys"""

    ty = EcdsaPrivateKey
    proto_ty = "ecdsa_private_key"
