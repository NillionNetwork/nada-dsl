from typing import List

from circuit_io import Party, Input, Output
from compiler_frontend import compile
from future.nada_types.integer import PublicInteger8, PublicBigInteger, SecretInteger8, SecretInteger16

from nada_types import NadaType, AllTypes

"""
Arrays have fixed size at compile time.
"""


class Array(NadaType):
    inner_type: AllTypes
    size: int


class ArrayType(List):
    def __init__(self, origin, nparams, *, inst=True, name=None):
        origin = Array
        super().__init__(origin, inst=inst, name=name)


"""
Vector don't have fixed size at compile time but have it at runtime.
"""


class Vector(NadaType):
    inner_type: AllTypes
    size: PublicBigInteger


class VectorType(List):
    pass


if __name__ == "__main__":
    party1 = Party(name="Party1")
    party2 = Party(name="Party2")
    my_int8 = PublicInteger8(Input(name="my_int", party=party1))
    my_int8_2 = SecretInteger8(Input(name="my_int_2", party=party2))
    my_int16 = SecretInteger16(Input(name="my_int_2", party=party2))

    new_int8 = my_int8 + my_int8_2
    new_int16 = new_int8.cast(to=SecretInteger16) + my_int16

    out = Output(new_int16, "my_output")

    compile([out], 'a.out')
