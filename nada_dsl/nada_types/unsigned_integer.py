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
from nada_dsl.nada_types.boolean import SecretBoolean, PublicBoolean
from typing import Union


@dataclass
class SecretBigUnsignedInteger(NadaType):
    def __add__(
        self, other: Union["SecretBigUnsignedInteger", "PublicBigUnsignedInteger"]
    ) -> "SecretBigUnsignedInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretBigUnsignedInteger) or isinstance(
            other, PublicBigUnsignedInteger
        ):
            return SecretBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(
        self, other: Union["SecretBigUnsignedInteger", "PublicBigUnsignedInteger"]
    ) -> "SecretBigUnsignedInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretBigUnsignedInteger) or isinstance(
            other, PublicBigUnsignedInteger
        ):
            return SecretBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(
        self, other: Union["SecretBigUnsignedInteger", "PublicBigUnsignedInteger"]
    ) -> "SecretBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretBigUnsignedInteger) or isinstance(
            other, PublicBigUnsignedInteger
        ):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(
        self, other: Union["SecretBigUnsignedInteger", "PublicBigUnsignedInteger"]
    ) -> "SecretBoolean":
        operation = GreaterThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretBigUnsignedInteger) or isinstance(
            other, PublicBigUnsignedInteger
        ):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

@dataclass
class PublicBigUnsignedInteger(NadaType):
    def __add__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __truediv__(
        self, other: "PublicBigUnsignedInteger"
    ) -> "PublicBigUnsignedInteger":
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __rshift__(
        self, other: "PublicBigUnsignedInteger"
    ) -> "PublicBigUnsignedInteger":
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(
        self, other: "PublicBigUnsignedInteger"
    ) -> "PublicBigUnsignedInteger":
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
