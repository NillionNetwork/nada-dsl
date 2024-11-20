from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    my_int1 = PublicInteger(Input(name="my_int1", party=party1))
    my_int2 = PublicInteger(Input(name="my_int2", party=party1))

    array = Array.new(my_int1, my_int1)

    # Store a scalar, a compound type and a literal.
    tup = NTuple.new([my_int1, array, my_int2])

    scalar = tup[0]
    array = tup[1]
    scalar2 = tup[2]

    @nada_fn
    def add(a: PublicInteger) -> PublicInteger:
        return a + my_int2

    result = array.reduce(add, Integer(0))

    return [Output(scalar + scalar2 + result, "my_output", party1)]
