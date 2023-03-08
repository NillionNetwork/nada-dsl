from dataclasses import dataclass
from typing import Union

from . import NadaType
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean


@dataclass
class SecretBigUnsignedInteger(NadaType):
    def __add__(self, other: "SecretBigUnsignedInteger") -> "SecretBigUnsignedInteger":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if type(other) == SecretBigUnsignedInteger:
            return SecretBigUnsignedInteger(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: "SecretBigUnsignedInteger") -> "SecretBigUnsignedInteger":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if type(other) == SecretBigUnsignedInteger:
            return SecretBigUnsignedInteger(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def __lt__(self, other: "SecretBigUnsignedInteger") -> "SecretBoolean":
        if type(other) == SecretBigUnsignedInteger:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise Exception(f"Cannot compare {self} with {other}")
