from circuit_io import Party, Input, Output
from compiler_frontend import compile
from future.nada_types.collections import Array
from future.nada_types.function import nada_fn
from future.nada_types.integer import PublicInteger8, SecretInteger8, SecretInteger16
from future.operations import unzip


def circuit_arrays():
    party1 = Party(name="Party1")
    party2 = Party(name="Party2")
    my_array_1 = Array(SecretInteger8(Input(name="my_array_1", party=party1)), size=10)
    my_array_2 = Array(SecretInteger8(Input(name="my_array_2", party=party2)), size=10)

    unziped = unzip(my_array_2.zip(my_array_1))

    @nada_fn
    def add(a: SecretInteger16, b: SecretInteger16) -> SecretInteger16:
        return a + b

    new_array = my_array_1.zip(my_array_2).map(add).reduce(add)

    out1 = Output(unziped, "zip.unzip.tuple")
    out2 = Output(new_array, "zip.map.reduce.array")

    compile([out1, out2], 'a.out')


def circuit_ints():
    party1 = Party(name="Party1")
    party2 = Party(name="Party2")
    my_int8 = PublicInteger8(Input(name="my_int", party=party1))
    my_int8_2 = SecretInteger8(Input(name="my_int_2", party=party2))
    my_int16 = SecretInteger16(Input(name="my_int_2", party=party2))

    new_int8 = my_int8 + my_int8_2
    new_int16 = new_int8.cast(to=SecretInteger16) + my_int16

    out = Output(new_int16, "my_output")

    compile([out], 'a.out')


if __name__ == "__main__":
    circuit_arrays()
