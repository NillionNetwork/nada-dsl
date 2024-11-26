import os.path

from nada_dsl import *

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "a": {
            "type": "integer"
        },
        "b": {
            "type": "boolean"
        },
        "c": {
            "type": "object",
            "properties": {
                "c": {
                    "type": "integer"
                }
            }
        },
        "d": {
            "type": "array",
            "items": {
                "type": "integer"
            },
            "size": 2
        },
        "e": {
            "type": "array",
            "prefixItems": [{"type":  "integer"}, {"type":  "boolean"}]
        },
        "f": {
            "type": "integer",
            "nada_type": "unsigned_integer"
        }
    },
    "required": [
        "a",
        "b"
    ],
    "additionalProperties": False
}

def nada_main():
    party1 = Party(name="Party1")
    doc = Document(Input(name="my_doc", party=party1), schema=schema)
    my_int = PublicInteger(Input(name="my_int", party=party1))
    doc.a
    doc.b
    doc.c
    doc.d
    doc.e
    return [Output(doc.a + my_int, "my_output", party1)]
