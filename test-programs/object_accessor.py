from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    my_int1 = PublicInteger(Input(name="my_int1", party=party1))
    my_int2 = PublicInteger(Input(name="my_int2", party=party1))

    array = Array.new(my_int1, my_int1)

    # Store a scalar, a compound type and a literal.
    object = Object.new({"a": my_int1, "b": array, "c": my_int2})

    scalar = object.a
    array = object.b
    scalar_2 = object.c

    def add(acc: PublicInteger, a: PublicInteger) -> PublicInteger:
        return acc + a

    sum = array.reduce(add, my_int2)

    return [Output(scalar + scalar_2 + sum, "my_output", party1)]
