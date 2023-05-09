from dataclasses import dataclass
from typing import Union

from . import NadaType
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean, PublicBoolean


@dataclass
class SecretBigInteger(NadaType):
    def __add__(self, other: "SecretBigInteger") -> "SecretBigInteger":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if type(other) == SecretBigInteger:
            return SecretBigInteger(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: "SecretBigInteger") -> "SecretBigInteger":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if type(other) == SecretBigInteger:
            return SecretBigInteger(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def __lt__(self, other: "SecretBigInteger") -> "SecretBoolean":
        if type(other) == SecretBigInteger:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise Exception(f"Cannot compare {self} with {other}")

@dataclass
class PublicBigInteger(NadaType):
    def __add__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if type(other) == PublicBigInteger:
            return PublicBigInteger(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: "PublicBigInteger") -> "PublicBigInteger":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if type(other) == PublicBigInteger:
            return PublicBigInteger(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def __lt__(self, other: "PublicBigInteger") -> "PublicBoolean":
        if type(other) == PublicBigInteger:
            return PublicBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise Exception(f"Cannot compare {self} with {other}")
