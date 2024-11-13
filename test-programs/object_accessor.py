from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    my_int1 = PublicInteger(Input(name="my_int1", party=party1))

    tup1 = Object.new({"a": Integer(42), "b": my_int1}) 

    left = tup1["a"]
    right = tup1["b"]

    return [Output(left + right, "my_output", party1)]
