# pylint:disable=W0401,W0614
"""The Nada Scalar type definitions."""

from dataclasses import dataclass
from typing import Union
from nada_dsl.operations import *
from nada_dsl.program_io import Literal
from nada_dsl import SourceRef
from . import NadaType, Mode, BaseType, OperationType

# Constant dictionary that stores all the Nada types and is use to
# convert from the (mode, base_type) representation to the concrete Nada type
# (Integer, SecretBoolean,...)
SCALAR_TYPES = {}


class ScalarType(NadaType):
    """The Nada Scalar type.
    This is the super class for all scalar types in Nada.
    These are:
        - Boolean, PublicBoolean, SecretBoolean
        - Integer, PublicInteger, SecretInteger
        - UnsignedInteger, PublicUnsignedInteger, SecretUnsignedInteger
    `ScalarType` provides common operation implementations for all the scalar types
    based on the typing rules of the Nada model.
    """

    base_type: BaseType
    mode: Mode

    def __init__(self, inner: OperationType, base_type: BaseType, mode: Mode):
        super().__init__(inner=inner)
        self.base_type = base_type
        self.mode = mode

    def __eq__(self, other):
        return equals_operation(
            "Equals", "==", self, other, lambda lhs, rhs: lhs == rhs
        )

    def __ne__(self, other):
        return equals_operation(
            "NotEquals", "!=", self, other, lambda lhs, rhs: lhs != rhs
        )


def equals_operation(
    operation, operator, left: ScalarType, right: ScalarType, f
) -> ScalarType:
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
                left=left, right=right, source_ref=SourceRef.back_frame()
            )
            return PublicBoolean(inner=operation)
        case Mode.SECRET:
            operation = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame()
            )
            return SecretBoolean(inner=operation)


def register_scalar_type(mode: Mode, base_type: BaseType):
    """Decorator used to register a new scalar type in the `SCALAR_TYPES` dictionary."""

    def decorator(scalar_type: ScalarType):
        SCALAR_TYPES[(mode, base_type)] = scalar_type
        scalar_type.mode = mode
        scalar_type.base_type = base_type
        return scalar_type

    return decorator


def new_scalar_type(mode: Mode, base_type: BaseType) -> ScalarType:
    """Returns the corresponding MIR Nada Type"""
    return SCALAR_TYPES.get((mode, base_type))


class NumericType(ScalarType):
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
            inner = Power(left=self, right=other, source_ref=SourceRef.back_frame())
            return new_scalar_type(mode, base_type)(inner)
        raise TypeError(f"Invalid operation: {self} ** {other}")

    def __lshift__(self, other):
        return shift_operation(
            "LeftShift", "<<", self, other, lambda lhs, rhs: lhs << rhs
        )

    def __rshift__(self, other):
        return shift_operation(
            "RightShift", ">>", self, other, lambda lhs, rhs: lhs >> rhs
        )

    def __lt__(self, other):
        return binary_relational_operation(
            "LessThan", "<", self, other, lambda lhs, rhs: lhs < rhs
        )

    def __gt__(self, other):
        return binary_relational_operation(
            "GreaterThan", ">", self, other, lambda lhs, rhs: lhs > rhs
        )

    def __le__(self, other):
        return binary_relational_operation(
            "LessOrEqualThan", "<=", self, other, lambda lhs, rhs: lhs <= rhs
        )

    def __ge__(self, other):
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
    operation, operator, left: ScalarType, right: ScalarType, f
) -> ScalarType:
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
            inner = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame()
            )
            return new_scalar_type(mode, base_type)(inner)


def shift_operation(
    operation, operator, left: ScalarType, right: ScalarType, f
) -> ScalarType:
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
            inner = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame()
            )
            return new_scalar_type(mode, base_type)(inner)


def binary_relational_operation(
    operation, operator, left: ScalarType, right: ScalarType, f
) -> ScalarType:
    """This function is an abstraction for the binary relational operations"""
    base_type = left.base_type
    if base_type != right.base_type or not base_type.is_numeric():
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right.mode.value]))
    match mode:
        case Mode.CONSTANT:
            return new_scalar_type(mode, BaseType.BOOLEAN)(f(left.value, right.value))
        case Mode.PUBLIC | Mode.SECRET:
            inner = globals()[operation](
                left=left, right=right, source_ref=SourceRef.back_frame()
            )
            return new_scalar_type(mode, BaseType.BOOLEAN)(inner)


def public_equals_operation(left: ScalarType, right: ScalarType) -> ScalarType:
    """This function is an abstraction for the public_equals operation for all types."""
    base_type = left.base_type
    if base_type != right.base_type:
        raise TypeError(f"Invalid operation: {left}.public_equals({right})")
    if Mode.CONSTANT in (left.mode, right.mode):
        raise TypeError(f"Invalid operation: {left}.public_equals({right})")

    return PublicBoolean(
        inner=PublicOutputEquality(
            left=left, right=right, source_ref=SourceRef.back_frame()
        )
    )


class BooleanType(ScalarType):
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

    def if_else(self, arg_0: ScalarType, arg_1: ScalarType) -> ScalarType:
        """This function implements the function 'if_else' for every class that extends 'BooleanType'."""
        base_type = arg_0.base_type
        if (
            base_type != arg_1.base_type
            or base_type == BaseType.BOOLEAN
            or self.mode == Mode.CONSTANT
        ):
            raise TypeError(f"Invalid operation: {self}.IfElse({arg_0}, {arg_1})")
        mode = Mode(max([self.mode.value, arg_0.mode.value, arg_1.mode.value]))
        inner = IfElse(
            this=self, arg_0=arg_0, arg_1=arg_1, source_ref=SourceRef.back_frame()
        )
        if mode == Mode.CONSTANT:
            mode = Mode.PUBLIC
        return new_scalar_type(mode, base_type)(inner)


def binary_logical_operation(
    operation, operator, left: ScalarType, right: ScalarType, f
) -> ScalarType:
    """This function is an abstraction for the logical operations."""
    base_type = left.base_type
    if base_type != right.base_type or not base_type == BaseType.BOOLEAN:
        raise TypeError(f"Invalid operation: {left} {operator} {right}")
    mode = Mode(max([left.mode.value, right.mode.value]))
    if mode == Mode.CONSTANT:
        return Boolean(value=bool(f(left.value, right.value)))
    if mode == Mode.PUBLIC:
        operation = globals()[operation](
            left=left, right=right, source_ref=SourceRef.back_frame()
        )
        return PublicBoolean(inner=operation)

    operation = globals()[operation](
        left=left, right=right, source_ref=SourceRef.back_frame()
    )
    return SecretBoolean(inner=operation)


@register_scalar_type(Mode.CONSTANT, BaseType.INTEGER)
class Integer(NumericType):
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

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)


@dataclass
@register_scalar_type(Mode.CONSTANT, BaseType.UNSIGNED_INTEGER)
class UnsignedInteger(NumericType):
    """The Nada Unsigned Integer type.

    Represents a constant (literal) unsigned integer."""

    def __init__(self, value):
        value = int(value)
        super().__init__(
            Literal(value=value, source_ref=SourceRef.back_frame()),
            BaseType.UNSIGNED_INTEGER,
            Mode.CONSTANT,
        )
        self.value = value

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)


@register_scalar_type(Mode.CONSTANT, BaseType.BOOLEAN)
class Boolean(BooleanType):
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

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

    def __invert__(self: "Boolean") -> "Boolean":
        return Boolean(value=bool(not self.value))


@register_scalar_type(Mode.PUBLIC, BaseType.INTEGER)
class PublicInteger(NumericType):
    """The Nada Public Unsigned Integer type.

    Represents a public unsigned integer in a program. This is a public variable
    evaluated at runtime."""

    def __init__(self, inner: NadaType):
        super().__init__(inner, BaseType.INTEGER, Mode.PUBLIC)

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

    def public_equals(
        self, other: Union["PublicInteger", "SecretInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for Public integer types."""
        return public_equals_operation(self, other)


@register_scalar_type(Mode.PUBLIC, BaseType.UNSIGNED_INTEGER)
class PublicUnsignedInteger(NumericType):
    """The Nada Public Integer type.

    Represents a public integer in a program. This is a public variable
    evaluated at runtime."""

    def __init__(self, inner: NadaType):
        super().__init__(inner, BaseType.UNSIGNED_INTEGER, Mode.PUBLIC)

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

    def public_equals(
        self, other: Union["PublicUnsignedInteger", "SecretUnsignedInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for Public unsigned integer types."""
        return public_equals_operation(self, other)


@dataclass
@register_scalar_type(Mode.PUBLIC, BaseType.BOOLEAN)
class PublicBoolean(BooleanType):
    """The Nada Public Boolean type.

    Represents a public boolean in a program. This is a public variable
    evaluated at runtime."""

    def __init__(self, inner: NadaType):
        super().__init__(inner, BaseType.BOOLEAN, Mode.PUBLIC)

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

    def __invert__(self: "PublicBoolean") -> "PublicBoolean":
        operation = Not(this=self, source_ref=SourceRef.back_frame())
        return PublicBoolean(inner=operation)

    def public_equals(
        self, other: Union["PublicUnsignedInteger", "SecretUnsignedInteger"]
    ) -> "PublicBoolean":
        """Implementation of public equality for Public boolean types."""
        return public_equals_operation(self, other)


@dataclass
@register_scalar_type(Mode.SECRET, BaseType.INTEGER)
class SecretInteger(NumericType):
    """The Nada secret integer type."""

    def __init__(self, inner: NadaType):
        super().__init__(inner, BaseType.INTEGER, Mode.SECRET)

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

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
            return SecretInteger(inner=operation)
        if isinstance(other, PublicUnsignedInteger):
            operation = TruncPr(
                left=self, right=other, source_ref=SourceRef.back_frame()
            )
            return SecretInteger(inner=operation)

        raise TypeError(f"Invalid operation: {self}.trunc_pr({other})")

    @classmethod
    def random(cls) -> "SecretInteger":
        """Random operation for Secret integers."""
        return SecretInteger(inner=Random(source_ref=SourceRef.back_frame()))

    def to_public(self: "SecretInteger") -> "PublicInteger":
        """Convert this secret integer into a public variable."""
        operation = Reveal(this=self, source_ref=SourceRef.back_frame())
        return PublicInteger(inner=operation)


@dataclass
@register_scalar_type(Mode.SECRET, BaseType.UNSIGNED_INTEGER)
class SecretUnsignedInteger(NumericType):
    """The Nada Secret Unsigned integer type."""

    def __init__(self, inner: NadaType):
        super().__init__(inner, BaseType.UNSIGNED_INTEGER, Mode.SECRET)

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

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
            return SecretUnsignedInteger(inner=operation)
        if isinstance(other, PublicUnsignedInteger):
            operation = TruncPr(
                left=self, right=other, source_ref=SourceRef.back_frame()
            )
            return SecretUnsignedInteger(inner=operation)

        raise TypeError(f"Invalid operation: {self}.trunc_pr({other})")

    @classmethod
    def random(cls) -> "SecretUnsignedInteger":
        """Generate a random secret unsigned integer."""
        return SecretUnsignedInteger(inner=Random(source_ref=SourceRef.back_frame()))

    def to_public(
        self: "SecretUnsignedInteger",
    ) -> "PublicUnsignedInteger":
        """Convert this secret into a public variable."""
        operation = Reveal(this=self, source_ref=SourceRef.back_frame())
        return PublicUnsignedInteger(inner=operation)


@dataclass
@register_scalar_type(Mode.SECRET, BaseType.BOOLEAN)
class SecretBoolean(BooleanType):
    """The SecretBoolean Nada MIR type."""

    def __init__(self, inner: NadaType):
        super().__init__(inner, BaseType.BOOLEAN, Mode.SECRET)

    def __eq__(self, other):
        return ScalarType.__eq__(self, other)

    def __invert__(self: "SecretBoolean") -> "SecretBoolean":
        operation = Not(this=self, source_ref=SourceRef.back_frame())
        return SecretBoolean(inner=operation)

    def to_public(self: "SecretBoolean") -> "PublicBoolean":
        """Convert this secret into a public variable."""
        operation = Reveal(this=self, source_ref=SourceRef.back_frame())
        return PublicBoolean(inner=operation)
