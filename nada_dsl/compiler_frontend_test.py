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


def create_input(clazz, name: str, party: str, **kwargs):
    return clazz(Input(name=name, party=Party(party)), **kwargs)


def create_collection(clazz, inner_input, size, **kwargs):
    return clazz(inner_input, size, **kwargs)


def create_output(root: AllTypes, name: str, party: str) -> Output:
    return Output(root, name, Party(party))


def test_root_conversion():
    input = create_input(SecretInteger, "input", "input_party")
    output = create_output(input, "output", "output_party")
    mir = nada_dsl_to_nada_mir([output])
    assert len(mir["parties"]) == 2
    assert len(mir["inputs"]) == 1
    assert len(mir["outputs"]) == 1
    assert "source_files" in mir

    mir_output = mir["outputs"][0]
    assert mir_output["name"] == "output"
    assert mir_output["type"] == {"Secret": {"Integer": None}}
    assert mir_output["party"] == "output_party"
    assert list(mir_output["inner"].keys()) == ["InputReference"]


def test_input_conversion():
    input = Input(name="input", party=Party("party"))
    inputs = {"party": {"input": (input, {"Secret": {"Integer": None}})}}
    converted_inputs = to_input_list(inputs)
    assert len(converted_inputs) == 1

    converted = converted_inputs[0]
    assert converted["name"] == "input"
    assert converted["party"] == "party"
    assert converted["type"] == {"Secret": {"Integer": None}}


def test_duplicated_inputs_checks():
    party = Party("party")
    left = SecretInteger(Input(name="left", party=party))
    right = SecretInteger(Input(name="left", party=party))
    new_int = left + right
    output = create_output(new_int, "output", "party")

    with pytest.raises(Exception):
        nada_dsl_to_nada_mir([output])


@pytest.mark.parametrize(
    ("input_type", "type_name", "kwargs"),
    [
        (SecretInteger, {"Secret": {"Integer": None}}, {}),
        (SecretBoolean, {"Secret": {"Boolean": None}}, {}),
        (PublicInteger, {"Public": {"Integer": None}}, {}),
        (PublicBoolean, {"Public": {"Boolean": None}}, {}),
    ],
)
def test_simple_type_conversion(input_type, type_name, kwargs):
    input = create_input(input_type, "name", "party", **kwargs)
    converted_input = to_type_dict(input)
    assert converted_input == type_name


def test_rational_type_conversion():
    input = create_input(SecretRational, "name", "party", digits=3)
    converted_input = to_type_dict(input)
    expected = {"Secret": {"Rational": {"digits": 3}}}
    assert converted_input == expected


@pytest.mark.parametrize(
    ("input_type", "type_name", "size"), [(Array, "Array", 10), (Vector, "Vector", 10)]
)
def test_array_type_conversion(input_type, type_name, size):
    inner_input = create_input(SecretInteger, "name", "party", **{})
    input = create_collection(input_type, inner_input, size, **{})
    converted_input = to_type_dict(input)
    assert list(converted_input.keys()) == [type_name]


@pytest.mark.parametrize(
    ("operator", "name", "ty"),
    [
        (operator.add, "Addition", {"Secret": {"Integer": None}}),
        (operator.sub, "Subtraction", {"Secret": {"Integer": None}}),
        (operator.mul, "Multiplication", {"Secret": {"Integer": None}}),
        (operator.lt, "LessThan", {"Secret": {"Boolean": None}}),
        (operator.gt, "GreaterThan", {"Secret": {"Boolean": None}}),
        (operator.le, "LessOrEqualThan", {"Secret": {"Boolean": None}}),
        (operator.ge, "GreaterOrEqualThan", {"Secret": {"Boolean": None}}),
    ],
)
def test_binary_operator(operator, name, ty):
    left = create_input(SecretInteger, "left", "party")
    right = create_input(SecretInteger, "right", "party")
    program_operation = operator(left, right)
    op = process_operation(program_operation)
    assert list(op.keys()) == [name]

    inner = op[name]

    assert input_reference(inner["left"]) == "left"
    assert input_reference(inner["right"]) == "right"
    assert inner["type"] == ty


@pytest.mark.parametrize(
    ("operator", "name", "ty"),
    [
        (operator.add, "Addition", {"Public": {"Integer": None}}),
        (operator.sub, "Subtraction", {"Public": {"Integer": None}}),
        (operator.mul, "Multiplication", {"Public": {"Integer": None}}),
        (operator.truediv, "Division", {"Public": {"Integer": None}}),
        (operator.mod, "Modulo", {"Public": {"Integer": None}}),
        (operator.rshift, "RightShift", {"Public": {"Integer": None}}),
        (operator.lshift, "LeftShift", {"Public": {"Integer": None}}),
        (operator.lt, "LessThan", {"Public": {"Boolean": None}}),
        (operator.gt, "GreaterThan", {"Public": {"Boolean": None}}),
        (operator.le, "LessOrEqualThan", {"Public": {"Boolean": None}}),
        (operator.ge, "GreaterOrEqualThan", {"Public": {"Boolean": None}}),
        (operator.eq, "Equals", {"Public": {"Boolean": None}}),
    ],
)
def test_binary_operator_public(operator, name, ty):
    left = create_input(PublicInteger, "left", "party")
    right = create_input(PublicInteger, "right", "party")
    program_operation = operator(left, right)
    op = process_operation(program_operation)
    assert list(op.keys()) == [name]

    inner = op[name]

    assert input_reference(inner["left"]) == "left"
    assert input_reference(inner["right"]) == "right"
    assert inner["type"] == ty


@pytest.mark.parametrize(
    ("operator", "name", "ty"),
    [
        (operator.add, "Addition", {"Secret": {"Integer": None}}),
        (operator.sub, "Subtraction", {"Secret": {"Integer": None}}),
        (operator.mul, "Multiplication", {"Secret": {"Integer": None}}),
    ],
)
def test_binary_operator_public_secret(operator, name, ty):
    left = create_input(PublicInteger, "left", "party")
    right = create_input(SecretInteger, "right", "party")
    program_operation = operator(left, right)
    op = process_operation(program_operation)
    assert list(op.keys()) == [name]

    inner = op[name]

    assert input_reference(inner["left"]) == "left"
    assert input_reference(inner["right"]) == "right"
    assert inner["type"] == ty


@pytest.mark.parametrize(
    ("operator", "name", "ty"),
    [
        (operator.add, "Addition", {"Secret": {"Integer": None}}),
        (operator.sub, "Subtraction", {"Secret": {"Integer": None}}),
        (operator.mul, "Multiplication", {"Secret": {"Integer": None}}),
    ],
)
def test_binary_operator_secret_public(operator, name, ty):
    left = create_input(SecretInteger, "left", "party")
    right = create_input(PublicInteger, "right", "party")
    program_operation = operator(left, right)
    op = process_operation(program_operation)
    assert list(op.keys()) == [name]

    inner = op[name]

    assert input_reference(inner["left"]) == "left"
    assert input_reference(inner["right"]) == "right"
    assert inner["type"] == ty


@pytest.mark.parametrize(
    "operator",
    [
        operator.add,
        operator.sub,
        operator.lt,
        operator.gt,
        operator.le,
        operator.ge,
    ],
)
def test_rational_digit_checks(operator):
    left = create_input(SecretRational, "left", "party", digits=3)
    right = create_input(SecretRational, "right", "party", digits=4)
    with pytest.raises(Exception):
        operator(left, right)


@pytest.mark.parametrize("operator", [operator.add, operator.sub, operator.lt])
def test_rational_digit_checks_public(operator):
    left = create_input(PublicRational, "left", "party", digits=3)
    right = create_input(PublicRational, "right", "party", digits=4)
    with pytest.raises(Exception):
        operator(left, right)


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
        "NadaTuple": {
            "left_type": {"Secret": {"Integer": None}},
            "right_type": {"Secret": {"Integer": None}},
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
        "NadaTuple": {
            "left_type": {
                "Array": {"inner_type": {"Secret": {"Integer": None}}, "size": 10}
            },
            "right_type": {
                "Array": {"inner_type": {"Secret": {"Integer": None}}, "size": 10}
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
    assert inner["type"][input_name]["inner_type"] == {"Secret": {"Integer": None}}


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_reduce(input_type, input_name):
    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    inner_input = create_input(SecretInteger, "inner", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    reduce_operation = left.reduce(nada_function)
    op = process_operation(reduce_operation)
    assert list(op.keys()) == ["Reduce"]
    inner = op["Reduce"]
    assert inner["fn"] in FUNCTIONS
    assert inner["type"] == {"Secret": {"Integer": None}}
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
    check_arg(args[0], "a", {"Secret": {"Integer": None}})
    check_arg(args[1], "b", {"Secret": {"Integer": None}})
    assert nada_function["return_type"] == {"Secret": {"Integer": None}}
    assert list(nada_function["inner"].keys()) == ["Addition"]
    addition = nada_function["inner"]["Addition"]
    check_nada_function_arg_ref(
        addition["left"], nada_function["id"], "a", {"Secret": {"Integer": None}}
    )
    check_nada_function_arg_ref(
        addition["right"], nada_function["id"], "b", {"Secret": {"Integer": None}}
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
    check_arg(args[0], "a", {"Secret": {"Integer": None}})
    check_arg(args[1], "b", {"Secret": {"Integer": None}})
    assert nada_function["return_type"] == {"Secret": {"Integer": None}}
    assert list(nada_function["inner"].keys()) == ["Addition"]
    addition = nada_function["inner"]["Addition"]
    assert input_reference(addition["right"]) == "c"
    assert list(addition["left"].keys()) == ["Addition"]
    addition = addition["left"]["Addition"]
    check_nada_function_arg_ref(
        addition["left"], nada_function["id"], "a", {"Secret": {"Integer": None}}
    )
    check_nada_function_arg_ref(
        addition["right"], nada_function["id"], "b", {"Secret": {"Integer": None}}
    )


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
    check_arg(args[0], "a", {"Secret": {"Integer": None}})
    check_arg(args[1], "b", {"Secret": {"Integer": None}})
    assert nada_function["return_type"] == {"Secret": {"Integer": None}}
    assert list(nada_function["inner"].keys()) == ["Addition"]
    addition = nada_function["inner"]["Addition"]
    assert input_reference(addition["right"]) == "d"
    assert list(addition["left"].keys()) == ["Addition"]
    addition = addition["left"]["Addition"]
    assert input_reference(addition["right"]) == "c"
    assert list(addition["left"].keys()) == ["Addition"]
    addition = addition["left"]["Addition"]
    check_nada_function_arg_ref(
        addition["left"], nada_function["id"], "a", {"Secret": {"Integer": None}}
    )
    check_nada_function_arg_ref(
        addition["right"], nada_function["id"], "b", {"Secret": {"Integer": None}}
    )


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [(Array, "Array"), (Vector, "Vector")],
)
def test_nada_function_using_matrix(input_type, input_name):
    @nada_fn
    def add(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    @nada_fn
    def matrix_addition(a: input_type[SecretInteger], b: input_type) -> SecretInteger:
        return a.zip(b).map(add).reduce(add)

    add_fn = to_fn_dict(add)
    matrix_addition_fn = to_fn_dict(matrix_addition)
    assert matrix_addition_fn["function"] == "matrix_addition"
    args = matrix_addition_fn["args"]
    assert len(args) == 2
    a_arg_type = {input_name: {"inner_type": {"Secret": {"Integer": None}}}}
    check_arg(args[0], "a", a_arg_type)
    b_arg_type = {input_name: {"inner_type": "T"}}
    check_arg(args[1], "b", b_arg_type)
    assert matrix_addition_fn["return_type"] == {"Secret": {"Integer": None}}

    assert list(matrix_addition_fn["inner"].keys()) == ["Reduce"]
    reduce_op = matrix_addition_fn["inner"]["Reduce"]
    reduce_op["function_id"] = add_fn["id"]
    reduce_op["type"] = {"Secret": {"Integer": None}}

    assert list(reduce_op["inner"].keys()) == ["Map"]
    map_op = reduce_op["inner"]["Map"]
    map_op["function_id"] = add_fn["id"]
    map_op["type"] = {
        input_name: {"inner_type": {"Secret": {"Integer": None}}, "size": None}
    }

    assert list(map_op["inner"].keys()) == ["Zip"]
    zip_op = map_op["inner"]["Zip"]

    check_nada_function_arg_ref(
        zip_op["left"], matrix_addition_fn["id"], "a", a_arg_type
    )
    check_nada_function_arg_ref(
        zip_op["right"], matrix_addition_fn["id"], "b", b_arg_type
    )
