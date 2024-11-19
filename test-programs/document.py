from nada_dsl import *


def nada_main():
    party1 = Party(name="Party1")
    doc = Document(Input(name="my_doc", party=party1), "doc.json")
    my_int = PublicInteger(Input(name="my_int", party=party1))

    return [Output(doc.a + my_int, "my_output", party1)]
