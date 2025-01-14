"""
Compilation tests.
"""

import base64
import os
import json
import pytest
from betterproto.lib.google.protobuf import Empty

from nada_mir_proto.nillion.nada.mir import v1 as proto_mir
from nada_mir_proto.nillion.nada.types import v1 as proto_ty
from nada_mir_proto.nillion.nada.operations import v1 as proto_op

from nada_dsl.ast_util import AST_OPERATIONS, OperationId
from nada_dsl.compile import compile_script, compile_string, print_output
from nada_dsl.errors import NotAllowedException


@pytest.fixture(autouse=True)
def clean_inputs():
    AST_OPERATIONS.clear()
    OperationId.reset()
    yield


def get_test_programs_folder():
    file_path = os.path.realpath(__file__)
    this_directory = os.path.dirname(file_path)
    if not this_directory.endswith("/"):
        this_directory = this_directory + "/"
    return this_directory + "../test-programs/"


def test_compile_sum_integers():
    mir_bytes = compile_script(f"{get_test_programs_folder()}/sum_integers.py").mir
    assert len(mir_bytes) > 0
    mir = proto_mir.ProgramMir().parse(mir_bytes)
    # The MIR operations look like this:
    # - 2 InputReference
    # - 1 LiteralReference for the initial accumulator
    # - 2 Additions, one for the first input reference and the literal,
    #   the other addition of this addition and the other input reference
    literal_id = 0
    input_ids = []
    additions = {}
    for entry in mir.operations:
        op_id, operation = entry.id, entry.operation
        if hasattr(operation, "literal_ref"):
            literal_id = op_id
            assert operation.type == proto_ty.NadaType(integer=Empty())
        elif hasattr(operation, "input_ref"):
            input_ids.append(op_id)
        elif (
            hasattr(operation, "binary")
            and operation.binary.variant == proto_op.BinaryOperationVariant.ADDITION
        ):
            additions[op_id] = operation.binary
        else:
            raise Exception(f"Unexpected operation: {operation}")

    assert literal_id != 0
    assert len(input_ids) == 2
    assert len(additions) == 2
    # Now lets check that the two additions are well constructed
    # left: input reference, right: literal
    first_addition_found = False
    # left: addition, right: input reference
    second_addition_found = False
    for addition in additions.values():
        left_id = addition.left
        right_id = addition.right
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

    def add(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    def add_times(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a * add(a, b)

    new_int = add_times(my_int1, my_int2)
    return [Output(new_int, "my_output", party1)]

"""
    encoded_program_str = base64.b64encode(bytes(program_str, "utf-8")).decode("utf_8")
    compile_string(encoded_program_str)


def test_compile_map_simple():
    mir_bytes = compile_script(f"{get_test_programs_folder()}/map_simple.py").mir
    assert len(mir_bytes) > 0
    mir = proto_mir.ProgramMir().parse(mir_bytes)

    assert len(mir.operations) == 2
    assert len(mir.functions) == 1
    function_id = mir.functions[0].id
    operations_found = 0
    array_input_id = 0
    map_inner = 0
    output_id = mir.outputs[0].operation_id
    function_op_id = 0
    for entry in mir.operations:
        op_id, operation = entry.id, entry.operation
        if hasattr(operation, "input_ref"):
            array_input_id = op_id
            assert operation.type == proto_ty.NadaType(
                array=proto_ty.Array(
                    size=3,
                    contained_type=proto_ty.NadaType(secret_integer=Empty()),
                )
            )

            operations_found += 1
        elif hasattr(operation, "map"):
            assert operation.map.fn == function_id
            map_inner = operation.map.child
            function_op_id = op_id
            operations_found += 1
        else:
            raise Exception(f"Unexpected operation: {operation}")

    assert map_inner > -1
    assert array_input_id > -1
    assert map_inner == array_input_id
    assert 0 < function_op_id == output_id


def test_compile_ecdsa_program():
    program_str = """
from nada_dsl import *

def nada_main():
    party1 = Party(name="Party1")
    private_key = EcdsaPrivateKey(Input(name="private_key", party=party1))
    digest = EcdsaDigestMessage(Input(name="digest", party=party1))

    new_int = private_key.ecdsa_sign(digest)
    return [Output(new_int, "my_output", party1)]
"""
    encoded_program_str = base64.b64encode(bytes(program_str, "utf-8")).decode("utf_8")
    mir_bytes = compile_string(encoded_program_str).mir
    assert len(mir_bytes) > 0


def test_compile_ntuple():
    mir_bytes = compile_script(f"{get_test_programs_folder()}/ntuple_accessor.py").mir
    assert len(mir_bytes) > 0


def test_compile_object():
    mir_str = compile_script(f"{get_test_programs_folder()}/object_accessor.py").mir
    assert len(mir_str) > 0
