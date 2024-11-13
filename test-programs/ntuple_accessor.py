from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    my_int1 = PublicInteger(Input(name="my_int1", party=party1))
    my_int2 = PublicInteger(Input(name="my_int2", party=party1))

    obj = Object.new({"a": Integer(42), "b": my_int1})
    arr = Array.new(my_int1, my_int1)
    tup1 = NTuple.new([my_int1, arr])

    old_tup2 = Tuple.new(arr, arr)
    print(f"##### old_tup2={old_tup2}")

    new_tup = NTuple.new([arr, arr])
    # new_tup2 = NTuple.new([new_tup, new_tup])
    print(f"##### new_tup={new_tup}")
    print(f"##### new_tup[0]={new_tup[0]}")

    sum = my_int1 + my_int2
    # print(f"##### sum={sum} left={sum.inner.left} right={sum.inner.right}")

    # print(f"##### arr={arr}")

    print(f"##### tup1[0]={tup1[0]}")
    print(f"##### tup1[1]={tup1[1]}")

    left = tup1[0]
    right = tup1[1]["b"]

    return [Output(left + right, "my_output", party1)]
