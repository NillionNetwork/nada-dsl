from dataclasses import dataclass
from typing import Union

from . import NadaType
from nada_dsl.operations import Addition, Multiplication
from nada_dsl.source_ref import SourceRef


@dataclass
class SecretBigInteger(NadaType):
    def __add__(self, other: Union["SecretBigInteger"]) -> Union["SecretBigInteger"]:
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if type(other) == SecretBigInteger:
            return SecretBigInteger(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: Union["SecretBigInteger"]) -> Union["SecretBigInteger"]:
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if type(other) == SecretBigInteger:
            return SecretBigInteger(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")
