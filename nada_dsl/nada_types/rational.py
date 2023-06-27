from dataclasses import dataclass

from . import NadaType
from nada_dsl.operations import Addition, Multiplication, LessThan, GreaterThan
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean, PublicBoolean


@dataclass
class SecretRational(NadaType):
    digits: int

    def __add__(self, other: "SecretRational") -> "SecretRational":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretRational) and other.digits == self.digits:
            return SecretRational(inner=addition, digits=self.digits)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(self, other: "SecretRational") -> "SecretRational":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretRational):
            digits = self.digits + other.digits
            return SecretRational(inner=multiplication, digits=digits)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(self, other: "SecretRational") -> "SecretBoolean":
        if isinstance(other, SecretRational) and other.digits == self.digits:
            return SecretBoolean(
                inner=LessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "SecretRational") -> "SecretBoolean":
        if isinstance(other, SecretRational) and other.digits == self.digits:
            return SecretBoolean(
                inner=GreaterThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")


@dataclass
class PublicRational(NadaType):
    digits: int

    def __add__(self, other: "PublicRational") -> "PublicRational":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicRational) and other.digits == self.digits:
            return PublicRational(inner=operation, digits=self.digits)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __mul__(self, other: "PublicRational") -> "PublicRational":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicRational):
            digits = self.digits + other.digits
            return PublicRational(inner=operation, digits=digits)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(self, other: "PublicRational") -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicRational) and other.digits == self.digits:
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicRational") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicRational) and other.digits == self.digits:
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")
