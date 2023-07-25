from dataclasses import dataclass
from typing import Union

from nada_dsl.nada_types.boolean import PublicBoolean, SecretBoolean
from nada_dsl.operations import (
    Addition,
    Division,
    Equals,
    GreaterOrEqualThan,
    GreaterThan,
    LeftShift,
    LessOrEqualThan,
    LessThan,
    Modulo,
    Multiplication,
    RightShift,
    Subtraction,
)
from nada_dsl.source_ref import SourceRef

from . import NadaType


@dataclass
class SecretInteger(NadaType):
    def __add__(
        self, other: Union["SecretInteger", "PublicInteger"]
    ) -> "SecretInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretInteger) or isinstance(other, PublicInteger):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretInteger", "PublicInteger"]
    ) -> "SecretInteger":
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger) or isinstance(other, PublicInteger):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretInteger", "PublicInteger"]
    ) -> "SecretInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger) or isinstance(other, PublicInteger):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")


@dataclass
class PublicInteger(NadaType):
    def __add__(
        self, other: Union["SecretInteger", "PublicInteger"]
    ) -> Union["SecretInteger", "PublicInteger"]:
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretInteger", "PublicInteger"]
    ) -> Union["SecretInteger", "PublicInteger"]:
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretInteger", "PublicInteger"]
    ) -> Union["SecretInteger", "PublicInteger"]:
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __truediv__(self, other: "PublicInteger") -> "PublicInteger":
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: "PublicInteger") -> "PublicInteger":
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __rshift__(self, other: "PublicInteger") -> "PublicInteger":
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(self, other: "PublicInteger") -> "PublicInteger":
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
