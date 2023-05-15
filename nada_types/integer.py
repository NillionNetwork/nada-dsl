from dataclasses import dataclass

from . import NadaType
from nada_dsl.operations import (
    Addition,
    CompareGreaterOrEqualThan,
    CompareGreaterThan,
    CompareLessOrEqualThan,
    CompareLessThan,
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


@dataclass
class SecretBigInteger(NadaType):
    def __add__(self, other: "SecretBigInteger") -> "SecretBigInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretBigInteger):
            return SecretBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(self, other: "SecretBigInteger") -> "SecretBigInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretBigInteger):
            return SecretBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(self, other: "SecretBigInteger") -> "SecretBoolean":
        operation = CompareLessThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretBigInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")


@dataclass
class PublicBigInteger(NadaType):
    def __add__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __div__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __rshift__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigInteger):
            return PublicBigInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: "PublicBigInteger") -> "PublicBoolean":
        operation = CompareLessThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicBigInteger") -> "PublicBoolean":
        operation = CompareGreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __lte__(self, other: "PublicBigInteger") -> "PublicBoolean":
        operation = CompareLessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __gte__(self, other: "PublicBigInteger") -> "PublicBoolean":
        operation = CompareGreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicBigInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
