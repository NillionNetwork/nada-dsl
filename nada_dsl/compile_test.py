"""
Compilation tests.
"""

import base64
import os
import json
import pytest
from nada_dsl.ast_util import AST_OPERATIONS
from nada_dsl.compile import compile_script, compile_string
from nada_dsl.compiler_frontend import FUNCTIONS, INPUTS, PARTIES
from nada_dsl.errors import NotAllowedException


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
    if not this_directory.endswith("/"):
        this_directory = this_directory + "/"
    return this_directory + "../test-programs/"


def test_compile_nada_fn_simple():
    mir_str = compile_script(f"{get_test_programs_folder()}/nada_fn_simple.py").mir
    assert mir_str != ""
    mir = json.loads(mir_str)
    mir_functions = mir["functions"]
    assert len(mir_functions) == 1


def test_compile_sum_integers():
    mir_str = compile_script(f"{get_test_programs_folder()}/sum_integers.py").mir
    assert mir_str != ""
    mir = json.loads(mir_str)
    # The MIR operations look like this:
    # - 2 InputReference
    # - 1 LiteralReference for the initial accumulator
    # - 2 Additions, one for the first input reference and the literal,
    #   the other addition of this addition and the other input reference
    literal_id = 0
    input_ids = []
    additions = {}
    for operation in mir["operations"].values():
        for name, op in operation.items():
            op_id = op["id"]
            if name == "LiteralReference":
                literal_id = op_id
                assert op["type"] == "Integer"
            elif name == "InputReference":
                input_ids.append(op_id)
            elif name == "Addition":
                additions[op_id] = op
            else:
                raise Exception(f"Unexpected operation: {name}")
    assert literal_id != 0
    assert len(input_ids) == 2
    assert len(additions) == 2
    # Now lets check that the two additions are well constructed
    # left: input reference, right: literal
    first_addition_found = False
    # left: addition, right: input reference
    second_addition_found = False
    for addition in additions.values():
        left_id = addition["left"]
        right_id = addition["right"]
        if left_id in input_ids and right_id == literal_id:
            first_addition_found = True
        if left_id in additions.keys() and right_id in input_ids:
            second_addition_found = True
    assert first_addition_found and second_addition_found


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


def test_compile_nada_fn_literals():
    with pytest.raises(NotAllowedException):
        mir_str = compile_script(f"{get_test_programs_folder()}/nada_fn_literal.py").mir


def test_compile_map_simple():
    mir_str = compile_script(f"{get_test_programs_folder()}/map_simple.py").mir
    assert mir_str != ""
    mir = json.loads(mir_str)
    assert len(mir["operations"]) == 2
    assert len(mir["functions"]) == 1
    function_id = mir["functions"][0]["id"]
    operations_found = 0
    array_input_id = 0
    map_inner = 0
    output_id = mir["outputs"][0]["operation_id"]
    function_op_id = 0
    for operation in mir["operations"].values():
        for name, op in operation.items():
            op_id = op["id"]
            if name == "InputReference":
                array_input_id = op_id
                assert op["type"] == {
                    "Array": {"inner_type": "SecretInteger", "size": 3}
                }
                operations_found += 1
            elif name == "Map":
                assert op["fn"] == function_id
                map_inner = op["inner"]
                function_op_id = op["id"]
                operations_found += 1
            else:
                raise Exception(f"Unexpected operation: {name}")
    assert map_inner > 0 and array_input_id > 0 and map_inner == array_input_id
    assert function_op_id > 0 and output_id == function_op_id
