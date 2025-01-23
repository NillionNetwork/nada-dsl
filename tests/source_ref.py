import sys
import os.path

from nada_dsl.compiler_frontend import nada_dsl_to_nada_mir, print_operations, print_mir
from nada_mir_proto.nillion.nada.mir.v1 import ProgramMir, SourceRef
from nada_dsl.errors import MissingEntryPointError, MissingProgramArgumentError
from tests.compile_test import get_test_programs_folder


def mir_model(script_path) -> ProgramMir:
    script_dir = os.path.dirname(script_path)
    sys.path.insert(0, script_dir)
    script_name = os.path.basename(script_path)
    if script_name.endswith(".py"):
        script_name = script_name[:-3]
    script = __import__(script_name)

    try:
        main = getattr(script, "nada_main")
    except Exception as exc:
        raise MissingEntryPointError(
            "'nada_dsl' entrypoint function is missing in program " + script_name
        ) from exc

    outputs = main()
    return nada_dsl_to_nada_mir(outputs)


def assert_source_ref(
    mir: ProgramMir, source_ref_index: int, file: str, lineno: int, offset: int, length: int
):
    source_ref = mir.source_refs[source_ref_index]
    assert source_ref.file == file
    assert source_ref.lineno == lineno
    assert source_ref.offset == offset
    assert source_ref.length == length


def test_multiple_operations():
    mir = mir_model(f"{get_test_programs_folder()}/multiple_operations.py")


    # party1 = Party(name="Party1")
    assert_source_ref(mir, mir.parties[0].source_ref_index, "multiple_operations.py", 6, 67, 33)

    # my_int1 = PublicInteger(Input(name="my_int1", party=party1))
    assert_source_ref(mir, mir.inputs[0].source_ref_index, "multiple_operations.py", 7, 101, 64)
    assert_source_ref(mir, mir.operations[0].operation.source_ref_index, "multiple_operations.py", 7, 101, 64)
    # my_int2 = PublicInteger(Input(name="my_int2", party=party1))
    assert_source_ref(mir, mir.inputs[1].source_ref_index, "multiple_operations.py", 8, 166, 64)
    assert_source_ref(mir, mir.operations[1].operation.source_ref_index, "multiple_operations.py", 8, 166, 64)

    # addition = my_int1 * my_int2
    assert_source_ref(mir, mir.operations[2].operation.source_ref_index, "multiple_operations.py", 10, 232, 32)
    # equals = my_int1 == my_int2
    assert_source_ref(mir, mir.operations[3].operation.source_ref_index, "multiple_operations.py", 11, 265, 31)
    # pow = my_int1**my_int2
    assert_source_ref(mir, mir.operations[4].operation.source_ref_index, "multiple_operations.py", 12, 297, 26)
    # sum_list = sum([my_int1, my_int2]) = 0 + my_int1 + my_int2
    # literal_ref
    assert_source_ref(mir, mir.operations[5].operation.source_ref_index, "multiple_operations.py", 13, 324, 38)
    # 0 + my_int1
    assert_source_ref(mir, mir.operations[6].operation.source_ref_index, "multiple_operations.py", 13, 324, 38)
    # 0 + my_int1 + my_int2
    assert_source_ref(mir, mir.operations[7].operation.source_ref_index, "multiple_operations.py", 13, 324, 38)
    # shift_l = my_int1 << UnsignedInteger(2)
    # literal_ref
    assert_source_ref(mir, mir.operations[8].operation.source_ref_index, "multiple_operations.py", 14, 363, 43)
    # my_int1 << UnsignedInteger(2)
    assert_source_ref(mir, mir.operations[9].operation.source_ref_index, "multiple_operations.py", 14, 363, 43)
    # shift_l = my_int1 >> UnsignedInteger(2)
    # literal_ref
    assert_source_ref(mir, mir.operations[10].operation.source_ref_index, "multiple_operations.py", 15, 407, 43)
    # my_int1 >> UnsignedInteger(2)
    assert_source_ref(mir, mir.operations[11].operation.source_ref_index, "multiple_operations.py", 15, 407, 43)
    # function_result = function(my_int1, my_int2) -> return a + b
    assert_source_ref(mir, mir.operations[12].operation.source_ref_index, "lib.py", 5, 104, 16)

    # Output(addition, "addition", party1),
    assert_source_ref(mir, mir.outputs[0].source_ref_index, "multiple_operations.py", 19, 514, 45)
    # Output(equals, "equals", party1),
    assert_source_ref(mir, mir.outputs[1].source_ref_index, "multiple_operations.py", 20, 560, 41)
    # Output(pow, "pow", party1),
    assert_source_ref(mir, mir.outputs[2].source_ref_index, "multiple_operations.py", 21, 602, 35)
    # Output(sum_list, "sum_list", party1),
    assert_source_ref(mir, mir.outputs[3].source_ref_index, "multiple_operations.py", 22, 638, 45)
    # Output(shift_l, "shift_l", party1),
    assert_source_ref(mir, mir.outputs[4].source_ref_index, "multiple_operations.py", 23, 684, 43)
    # Output(shift_r, "shift_r", party1),
    assert_source_ref(mir, mir.outputs[5].source_ref_index, "multiple_operations.py", 24, 728, 43)
    # Output(function_result, "function_result", party1),
    assert_source_ref(mir, mir.outputs[6].source_ref_index, "multiple_operations.py", 25, 772, 59)
