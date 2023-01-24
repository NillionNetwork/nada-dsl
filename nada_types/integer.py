from dataclasses import dataclass
from inspect import currentframe
from typing import Union

from nada_types import NadaType
from operations import Addition, Multiplication


@dataclass
class SecretBigInteger(NadaType):
    def __add__(self, other: Union['SecretBigInteger']) -> Union['SecretBigInteger']:
        addition = Addition(right=self, left=other, back_stackframe=currentframe().f_back)
        if type(other) == SecretBigInteger:
            return SecretBigInteger(inner=addition)
        else:
            raise Exception(f"Cannot add {self} {other}")

    def __mul__(self, other: Union['SecretBigInteger']) -> Union['SecretBigInteger']:
        multiplication = Multiplication(right=self, left=other, back_stackframe=currentframe().f_back)
        if type(other) == SecretBigInteger:
            return SecretBigInteger(inner=multiplication)
        else:
            raise Exception(f"Cannot multiply {self} * {other}")
