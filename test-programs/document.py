from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    my_document = PublicDocument(Input(name="my_doc", party=party1), "source.json")
    my_int = PublicInteger(Input(name="my_int", party=party1))

    out = Output(my_document.foo + my_document.bar + my_int, "my_output", party1)

    return [out]
