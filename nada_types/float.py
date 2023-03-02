from dataclasses import dataclass
from typing import Union

from . import NadaType
from nada_dsl.operations import Addition, Multiplication, CompareLessThan
from nada_dsl.source_ref import SourceRef
from nada_dsl.nada_types.boolean import SecretBoolean


@dataclass
class SecretFixedFloatPoint(NadaType):
    decimals: int

    def __add__(self, other: "SecretFixedFloatPoint") -> "SecretFixedFloatPoint":
        addition = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if type(other) == SecretFixedFloatPoint and other.decimals == self.decimals:
            return SecretFixedFloatPoint(inner=addition, decimals=self.decimals)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: "SecretFixedFloatPoint") -> "SecretFixedFloatPoint":
        multiplication = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if type(other) == SecretFixedFloatPoint and other.decimals == self.decimals:
            return SecretFixedFloatPoint(inner=multiplication, decimals=self.decimals)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")

    def __lt__(self, other: "SecretFixedFloatPoint") -> "SecretBoolean":
        if type(other) == SecretFixedFloatPoint and other.decimals == self.decimals:
            return SecretBoolean(
                inner=CompareLessThan(
                    left=self, right=other, source_ref=SourceRef.back_frame()
                )
            )
        else:
            raise Exception(f"Cannot compare {self} with {other}")
