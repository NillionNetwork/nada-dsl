"""
Compilation tests.
"""

import base64
import os
import json
import pytest
from nada_dsl.ast_util import AST_OPERATIONS
from nada_dsl.compile import compile, compile_string
from nada_dsl.compiler_frontend import FUNCTIONS, INPUTS, PARTIES

@pytest.fixture(autouse=True)
def clean_inputs():
    PARTIES.clear()
    INPUTS.clear()
    FUNCTIONS.clear()
    AST_OPERATIONS.clear()
    yield

def get_test_programs_folder():
    file_path = os.path.realpath(__file__)
    this_directory = os.path.dirname(file_path)
    return this_directory + "/../../test-programs/programs"


def test_compile_nada_fn_simple():
    mir_str = compile(f"{get_test_programs_folder()}/nada_fn_simple.py").mir
    assert mir_str != ""
    mir = json.loads(mir_str)
    mir_functions = mir["functions"]
    assert len(mir_functions) == 1


def test_compile_nada_fn_compound():
    program_str = """
from nada_dsl import *

def nada_main():
    party1 = Party(name="Party1")
    my_int1 = SecretInteger(Input(name="my_int1", party=party1))
    my_int2 = SecretInteger(Input(name="my_int2", party=party1))

    @nada_fn
    def add(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    @nada_fn
    def add_times(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a * add(a, b)

    new_int = add_times(my_int1, my_int2)
    return [Output(new_int, "my_output", party1)]

"""
    encoded_program_str = base64.b64encode(bytes(program_str, "utf-8")).decode("utf_8")
    compile_string(encoded_program_str)


# TODO recursive programs fail with `NameError` for now. This is incorrect.
def test_compile_program_with_recursion():
    program_str = """from nada_dsl import *

def nada_main():
    party1 = Party(name="Party1")
    my_int1 = SecretInteger(Input(name="my_int1", party=party1))
    my_int2 = SecretInteger(Input(name="my_int2", party=party1))

    @nada_fn
    def add_times(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a * add_times(a, b)

    new_int = add_times(my_int1, my_int2)
    return [Output(new_int, "my_output", party1)]
"""
    encoded_program_str = base64.b64encode(bytes(program_str, "utf-8")).decode("utf_8")

    with pytest.raises(NameError):
        compile_string(encoded_program_str)
