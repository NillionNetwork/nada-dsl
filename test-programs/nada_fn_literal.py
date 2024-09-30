from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")

    @nada_fn
    def add(a: Integer, b: Integer) -> Integer:
        return a + b

    new_int = add(Integer(2), Integer(-5))
    return [Output(new_int, "my_output", party1)]
