"""
Compiler frontend tests.
"""
import pytest
import operator

from nada_dsl import *
from nada_dsl.compiler_frontend import (
    nada_dsl_to_nada_mir,
    to_input_list,
    to_type_dict,
    to_fn_dict,
    process_operation,
    INPUTS,
    PARTIES,
    FUNCTIONS,
)


@pytest.fixture(autouse=True)
def clean_inputs():
    PARTIES.clear()
    INPUTS.clear()
    FUNCTIONS.clear()
    yield


def input_reference(ref) -> str:
    return ref["InputReference"]["refers_to"]


def literal_reference(ref) -> str:
    return ref["LiteralReference"]["refers_to"]


def create_input(cls, name: str, party: str, **kwargs):
    return cls(Input(name=name, party=Party(party)), **kwargs)


def create_literal(cls, value: Any, **kwargs):
    return cls(value=value, **kwargs)


def create_collection(cls, inner_input, size, **kwargs):
    return cls(inner_input, size, **kwargs)


def create_output(root: AllTypes, name: str, party: str) -> Output:
    return Output(root, name, Party(party))

def to_type(name: str):
    # Rename public variables so they are considered as the same as literals.
    if name.startswith("Public"):
        name = name[len("Public") :].lstrip()
        return name
    else:
        return name

# Generated tests are added below this line. Please leave it as it is.


def test_root_conversion():
    input = create_input(SecretInteger, "input", "input_party")
    output = create_output(input, "output", "output_party")
    mir = nada_dsl_to_nada_mir([output])
    assert len(mir["parties"]) == 2
    assert len(mir["inputs"]) == 1
    assert len(mir["literals"]) == 0
    assert len(mir["outputs"]) == 1
    assert "source_files" in mir

    mir_output = mir["outputs"][0]
    assert mir_output["name"] == "output"
    assert mir_output["type"] == "SecretInteger"
    assert mir_output["party"] == "output_party"
    assert list(mir_output["inner"].keys()) == ["InputReference"]


def test_input_conversion():
    input = Input(name="input", party=Party("party"))
    inputs = {"party": {"input": (input, "SecretInteger")}}
    converted_inputs = to_input_list(inputs)
    assert len(converted_inputs) == 1

    converted = converted_inputs[0]
    assert converted["name"] == "input"
    assert converted["party"] == "party"
    assert converted["type"] == "SecretInteger"


def test_duplicated_inputs_checks():
    party = Party("party")
    left = SecretInteger(Input(name="left", party=party))
    right = SecretInteger(Input(name="left", party=party))
    new_int = left + right
    output = create_output(new_int, "output", "party")

    with pytest.raises(Exception):
        nada_dsl_to_nada_mir([output])


@pytest.mark.parametrize(
    ("input_type", "type_name", "size"), [(Array, "Array", 10), (Vector, "Vector", 10)]
)
def test_array_type_conversion(input_type, type_name, size):
    inner_input = create_input(SecretInteger, "name", "party", **{})
    input = create_collection(input_type, inner_input, size, **{})
    converted_input = to_type_dict(input)
    assert list(converted_input.keys()) == [type_name]


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_zip(input_type, input_name):
    inner_input = create_input(SecretInteger, "left", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    inner_input = create_input(SecretInteger, "right", "party", **{})
    right = create_collection(input_type, inner_input, 10, **{})
    zipped = left.zip(right)
    op = process_operation(zipped)
    assert list(op.keys()) == ["Zip"]

    inner = op["Zip"]

    assert input_reference(inner["left"]) == "left"
    assert input_reference(inner["right"]) == "right"
    assert inner["type"][input_name]["inner_type"] == {
        "Tuple": {
            "left_type": "SecretInteger",
            "right_type": "SecretInteger",
        }
    }


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_unzip(input_type, input_name):
    inner_input = create_input(SecretInteger, "left", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    inner_input = create_input(SecretInteger, "right", "party", **{})
    right = create_collection(input_type, inner_input, 10, **{})
    unzipped = unzip(left.zip(right))
    op = process_operation(unzipped)

    assert list(op.keys()) == ["Unzip"]

    inner = op["Unzip"]

    assert list(inner["inner"].keys()) == [
        "Zip"
    ]  # We don't check Zip operation because it has its test
    assert inner["type"] == {
        "Tuple": {
            "left_type": {
                "Array": {"inner_type": "SecretInteger", "size": 10}
            },
            "right_type": {
                "Array": {"inner_type": "SecretInteger", "size": 10}
            },
        }
    }


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_map(input_type, input_name):
    @nada_fn
    def nada_function(a: SecretInteger) -> SecretInteger:
        return a + a

    inner_input = create_input(SecretInteger, "inner", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    map_operation = left.map(nada_function)
    op = process_operation(map_operation)
    assert list(op.keys()) == ["Map"]
    inner = op["Map"]
    assert inner["fn"] in FUNCTIONS
    assert list(inner["type"].keys()) == [input_name]
    assert input_reference(inner["inner"]) == "inner"
    assert inner["type"][input_name]["inner_type"] == "SecretInteger"


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_reduce(input_type, input_name):
    c = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    inner_input = create_input(SecretInteger, "inner", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    reduce_operation = left.reduce(nada_function, c)
    op = process_operation(reduce_operation)
    assert list(op.keys()) == ["Reduce"]
    inner = op["Reduce"]
    assert inner["fn"] in FUNCTIONS
    assert inner["type"] == "SecretInteger"
    assert input_reference(inner["inner"]) == "inner"


def check_arg(arg: NadaFunctionArg, arg_name, arg_type):
    assert arg["name"] == arg_name
    assert arg["type"] == arg_type


def check_nada_function_arg_ref(arg_ref, function_id, name, ty):
    assert list(arg_ref.keys()) == ["NadaFunctionArgRef"]
    assert arg_ref["NadaFunctionArgRef"]["function_id"] == function_id
    assert arg_ref["NadaFunctionArgRef"]["refers_to"] == name
    assert arg_ref["NadaFunctionArgRef"]["type"] == ty


def test_nada_function_simple():
    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    nada_function = to_fn_dict(nada_function)
    assert nada_function["function"] == "nada_function"
    args = nada_function["args"]
    assert len(args) == 2
    check_arg(args[0], "a", "SecretInteger")
    check_arg(args[1], "b", "SecretInteger")
    assert nada_function["return_type"] == "SecretInteger"
    assert list(nada_function["body"].keys()) == ["Addition"]
    addition = nada_function["body"]["Addition"]
    check_nada_function_arg_ref(
        addition["left"], nada_function["id"], "a", "SecretInteger"
    )
    check_nada_function_arg_ref(
        addition["right"], nada_function["id"], "b", "SecretInteger"
    )


def test_nada_function_using_inputs():
    c = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b + c

    nada_function = to_fn_dict(nada_function)
    assert nada_function["function"] == "nada_function"
    args = nada_function["args"]
    assert len(args) == 2
    check_arg(args[0], "a", "SecretInteger")
    check_arg(args[1], "b", "SecretInteger")
    assert nada_function["return_type"] == "SecretInteger"
    assert list(nada_function["body"].keys()) == ["Addition"]
    addition = nada_function["body"]["Addition"]
    assert input_reference(addition["right"]) == "c"
    assert list(addition["left"].keys()) == ["Addition"]
    addition = addition["left"]["Addition"]
    check_nada_function_arg_ref(
        addition["left"], nada_function["id"], "a", "SecretInteger"
    )
    check_nada_function_arg_ref(
        addition["right"], nada_function["id"], "b", "SecretInteger"
    )


def test_nada_function_call():
    c = create_input(SecretInteger, "c", "party", **{})
    d = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    nada_fn_call_return = nada_function(c, d)
    nada_fn_type = to_fn_dict(nada_function)

    nada_function_call = nada_fn_call_return.inner
    assert isinstance(nada_function_call, NadaFunctionCall)
    assert nada_function_call.fn.id == nada_fn_type["id"]


def test_nada_function_using_operations():
    c = create_input(SecretInteger, "c", "party", **{})
    d = create_input(SecretInteger, "d", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b + c + d

    nada_function = to_fn_dict(nada_function)
    assert nada_function["function"] == "nada_function"
    args = nada_function["args"]
    assert len(args) == 2
    check_arg(args[0], "a", "SecretInteger")
    check_arg(args[1], "b", "SecretInteger")
    assert nada_function["return_type"] == "SecretInteger"
    assert list(nada_function["body"].keys()) == ["Addition"]
    addition = nada_function["body"]["Addition"]
    assert input_reference(addition["right"]) == "d"
    assert list(addition["left"].keys()) == ["Addition"]
    addition = addition["left"]["Addition"]
    assert input_reference(addition["right"]) == "c"
    assert list(addition["left"].keys()) == ["Addition"]
    addition = addition["left"]["Addition"]
    check_nada_function_arg_ref(
        addition["left"], nada_function["id"], "a", "SecretInteger"
    )
    check_nada_function_arg_ref(
        addition["right"], nada_function["id"], "b", "SecretInteger"
    )


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_nada_function_using_matrix(input_type, input_name):
    c = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def add(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    @nada_fn
    def matrix_addition(a: input_type[SecretInteger], b: input_type) -> SecretInteger:
        return a.zip(b).map(add).reduce(add, c)

    add_fn = to_fn_dict(add)
    matrix_addition_fn = to_fn_dict(matrix_addition)
    assert matrix_addition_fn["function"] == "matrix_addition"
    args = matrix_addition_fn["args"]
    assert len(args) == 2
    a_arg_type = {input_name: {"inner_type": "SecretInteger"}}
    check_arg(args[0], "a", a_arg_type)
    b_arg_type = {input_name: {"inner_type": "T"}}
    check_arg(args[1], "b", b_arg_type)
    assert matrix_addition_fn["return_type"] == "SecretInteger"

    assert list(matrix_addition_fn["body"].keys()) == ["Reduce"]
    reduce_op = matrix_addition_fn["body"]["Reduce"]
    reduce_op["function_id"] = add_fn["id"]
    reduce_op["type"] = "SecretInteger"

    assert list(reduce_op["inner"].keys()) == ["Map"]
    map_op = reduce_op["inner"]["Map"]
    map_op["function_id"] = add_fn["id"]
    map_op["type"] = {
        input_name: {"inner_type": "SecretInteger", "size": None}
    }

    assert list(map_op["inner"].keys()) == ["Zip"]
    zip_op = map_op["inner"]["Zip"]

    check_nada_function_arg_ref(
        zip_op["left"], matrix_addition_fn["id"], "a", a_arg_type
    )
    check_nada_function_arg_ref(
        zip_op["right"], matrix_addition_fn["id"], "b", b_arg_type
    )


def test_array_new():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(SecretInteger, "second", "party", **{})
    array = Array.new(first_input, second_input)
    op = process_operation(array)

    assert list(op.keys()) == ["New"]

    inner = op["New"]

    assert input_reference(inner["elements"][0]) == "first"
    assert input_reference(inner["elements"][1]) == "second"
    assert inner["type"]["Array"] == {
        "inner_type": "SecretInteger",
        "size": 2,
    }


def test_array_new_empty():
    with pytest.raises(ValueError) as e:
        Array.new()
    assert str(e.value) == "At least one value is required"


def test_array_new_same_type():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(SecretUnsignedInteger, "second", "party", **{})

    with pytest.raises(TypeError) as e:
        Array.new(first_input, second_input)
    assert str(e.value) == "All arguments must be of the same type"


def test_tuple_new():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(PublicInteger, "second", "party", **{})
    array = Tuple.new(first_input, second_input)
    op = process_operation(array)

    assert list(op.keys()) == ["New"]

    inner = op["New"]

    assert input_reference(inner["elements"][0]) == "first"
    assert input_reference(inner["elements"][1]) == "second"
    assert inner["type"]["Tuple"] == {
        "left_type": "SecretInteger",
        "right_type": "Integer",
    }


def test_tuple_new_empty():
    with pytest.raises(TypeError) as e:
        Tuple.new()
    assert str(e.value) == "Tuple.new() missing 2 required positional arguments: 'left_type' and 'right_type'"
