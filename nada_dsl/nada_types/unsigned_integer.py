from dataclasses import dataclass

from . import NadaType
from nada_dsl.operations import (
    Addition,
    GreaterOrEqualThan,
    GreaterThan,
    LessOrEqualThan,
    LessThan,
    Division,
    Equals,
    LeftShift,
    Modulo,
    Multiplication,
    RightShift,
    Subtraction,
)
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean, PublicBoolean, Boolean
from typing import Literal, Union

@dataclass
class UnsignedInteger(NadaType):
    value: int

    def __init__(self, value: int):
        super().__init__(inner=Literal(value=value, source_ref=SourceRef.back_frame()))
        if isinstance(value, int):
            self.value = value
        else:
            raise ValueError(f"Expected an integer, got {type(value).__name__}")

    def __add__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]:
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        elif isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value + other.value)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]:
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        elif isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value - other.value)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]:
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        elif isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value * other.value)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __truediv__(self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]) -> Union["PublicUnsignedInteger", "UnsignedInteger"]:
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value / other.value)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]) -> Union["PublicUnsignedInteger", "UnsignedInteger"]:
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value % other.value)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __rshift__(self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]) -> Union["PublicUnsignedInteger", "UnsignedInteger"]:
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value >> other.value)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]) -> Union["PublicUnsignedInteger", "UnsignedInteger"]:
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return UnsignedInteger(value=self.value << other.value)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: Union["PublicUnsignedInteger", "UnsignedInteger"]) -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return Boolean(value=self.value < other.value)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return Boolean(value=self.value > other.value)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return Boolean(value=self.value <= other.value)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return Boolean(value=self.value >= other.value)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, UnsignedInteger):
            return Boolean(value=self.value == other.value)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")


@dataclass
class SecretUnsignedInteger(NadaType):
    def __add__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> "SecretUnsignedInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if (
            isinstance(other, SecretUnsignedInteger)
            or isinstance(other, PublicUnsignedInteger)
            or isinstance(other, UnsignedInteger)
        ):
            return SecretUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> "SecretUnsignedInteger":
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if (
            isinstance(other, SecretUnsignedInteger)
            or isinstance(other, PublicUnsignedInteger)
            or isinstance(other, UnsignedInteger)
        ):
            return SecretUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> "SecretUnsignedInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if (
            isinstance(other, SecretUnsignedInteger)
            or isinstance(other, PublicUnsignedInteger)
            or isinstance(other, UnsignedInteger)
        ):
            return SecretUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(self, other: "SecretUnsignedInteger") -> "SecretBoolean":
        # LT actually works differently for unsigned types, these are not correct.
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretUnsignedInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "SecretUnsignedInteger") -> "SecretBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "SecretUnsignedInteger") -> "SecretBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "SecretUnsignedInteger") -> "SecretBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")
    
    def __mod__(self, other: "PublicUnsignedInteger") -> "SecretUnsignedInteger":
        """Modulo operation for SecretUnsignedInteger.

        Only public divisor is supported.

        :param other: The modulo divisor, must be a public integer.
        :type other: PublicUnsignedInteger
        :raises TypeError: Raised when the divisor type is not PublicUnsignedInteger
        :return: The modulo result as a SecretUnsignedInteger
        :rtype: SecretUnsignedInteger
        """
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")


@dataclass
class PublicUnsignedInteger(NadaType):
    def __add__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> Union["SecretUnsignedInteger", "PublicUnsignedInteger"]:
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        elif isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> Union["SecretUnsignedInteger", "PublicUnsignedInteger"]:
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        elif isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretUnsignedInteger", "PublicUnsignedInteger", "UnsignedInteger"]
    ) -> Union["SecretUnsignedInteger", "PublicUnsignedInteger"]:
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretUnsignedInteger):
            return SecretUnsignedInteger(inner=operation)
        elif isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __truediv__(self, other: "PublicUnsignedInteger") -> "PublicUnsignedInteger":
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: "PublicUnsignedInteger") -> "PublicUnsignedInteger":
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __rshift__(self, other: "PublicUnsignedInteger") -> "PublicUnsignedInteger":
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(self, other: "PublicUnsignedInteger") -> "PublicUnsignedInteger":
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicUnsignedInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicUnsignedInteger) or isinstance(other, UnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
