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

    def add(acc: PublicInteger, a: PublicInteger) -> PublicInteger:
        return a + acc

    result = array.reduce(add, my_int1)

    scalar_sum = scalar + scalar2

    final = result + scalar_sum

    return [Output(final, "my_output", party1)]


if __name__ == "__main__":
    nada_main()
