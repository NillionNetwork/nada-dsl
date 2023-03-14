from dataclasses import dataclass
from typing import Union

from . import NadaType
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean


@dataclass
class SecretFixedPointRational(NadaType):
    digits: int

    def __add__(self, other: "SecretFixedPointRational") -> "SecretFixedPointRational":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if type(other) == SecretFixedPointRational and other.digits == self.digits:
            return SecretFixedPointRational(inner=addition, digits=self.digits)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: "SecretFixedPointRational") -> "SecretFixedPointRational":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if type(other) == SecretFixedPointRational:
            digits = self.digits+other.digits
            return SecretFixedPointRational(inner=multiplication, digits=digits)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def __lt__(self, other: "SecretFixedPointRational") -> "SecretBoolean":
        if type(other) == SecretFixedPointRational and other.digits == self.digits:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise Exception(f"Cannot compare {self} with {other}")
