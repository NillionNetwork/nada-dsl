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
class SecretBigUnsignedInteger(NadaType):
    def __add__(self, other: "SecretBigUnsignedInteger") -> "SecretBigUnsignedInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretBigUnsignedInteger):
            return SecretBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot add {self} and {other}")

    def __mul__(self, other: "SecretBigUnsignedInteger") -> "SecretBigUnsignedInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretBigUnsignedInteger):
            return SecretBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot multiply {self} and {other}")

    def __lt__(self, other: "SecretBigUnsignedInteger") -> "SecretBoolean":
        operation = CompareLessThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretBigUnsignedInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")


@dataclass
class PublicBigUnsignedInteger(NadaType):
    def __add__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot add {self} and {other}")

    def __sub__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot subtract {self} and {other}")

    def __mul__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot multiply {self} and {other}")

    def __div__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot divide {self} and {other}")

    def __mod__(self, other: "PublicBigUnsignedInteger") -> "PublicBigUnsignedInteger":
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot calculate the modulo of {self} and {other}")

    def __rshift__(
        self, other: "PublicBigUnsignedInteger"
    ) -> "PublicBigUnsignedInteger":
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot calculate the modulo of {self} and {other}")

    def __lshift__(
        self, other: "PublicBigUnsignedInteger"
    ) -> "PublicBigUnsignedInteger":
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBigUnsignedInteger(inner=operation)
        else:
            raise TypeError(f"Cannot calculate the modulo of {self} and {other}")

    def __lt__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = CompareLessThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")

    def __gt__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = CompareGreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")

    def __lte__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = CompareLessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")

    def __gte__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = CompareGreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")

    def __eq__(self, other: "PublicBigUnsignedInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBigUnsignedInteger):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")
