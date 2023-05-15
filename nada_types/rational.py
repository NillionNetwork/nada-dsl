from dataclasses import dataclass

from . import NadaType
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean, PublicBoolean


@dataclass
class SecretFixedPointRational(NadaType):
    digits: int

    def __add__(self, other: "SecretFixedPointRational") -> "SecretFixedPointRational":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretFixedPointRational) and other.digits == self.digits:
            return SecretFixedPointRational(inner=addition, digits=self.digits)
        else:
            raise TypeError(f"Cannot add {self} and {other}")

    def __mul__(self, other: "SecretFixedPointRational") -> "SecretFixedPointRational":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretFixedPointRational):
            digits = self.digits + other.digits
            return SecretFixedPointRational(inner=multiplication, digits=digits)
        else:
            raise TypeError(f"Cannot multiply {self} and {other}")

    def __lt__(self, other: "SecretFixedPointRational") -> "SecretBoolean":
        if isinstance(other, SecretFixedPointRational) and other.digits == self.digits:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Cannot compare {self} and {other}")


@dataclass
class PublicFixedPointRational(NadaType):
    digits: int

    def __add__(self, other: "PublicFixedPointRational") -> "PublicFixedPointRational":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicFixedPointRational) and other.digits == self.digits:
            return PublicFixedPointRational(inner=operation, digits=self.digits)
        else:
            raise TypeError(f"Cannot add {self} and {other}")

    def __mul__(self, other: "PublicFixedPointRational") -> "PublicFixedPointRational":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicFixedPointRational):
            digits = self.digits + other.digits
            return PublicFixedPointRational(inner=operation, digits=digits)
        else:
            raise TypeError(f"Cannot multiply {self} and {other}")

    def __lt__(self, other: "PublicFixedPointRational") -> "PublicBoolean":
        operation = CompareLessThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicFixedPointRational) and other.digits == self.digits:
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Cannot compare {self} and {other}")
