import pytest
import operator

from nada_dsl import *
from nada_dsl.compiler_frontend import (
    nada_dsl_to_nada_mir,
    to_input_list,
    to_type_dict,
    process_operation,
    INPUTS,
    PARTIES,
)


@pytest.fixture(autouse=True)
def clean_inputs():
    PARTIES.clear()
    INPUTS.clear()
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
    ("input_type", "type_name", "kwargs"),
    [
        (SecretInteger, "SecretInteger", {}),
        (SecretBoolean, "SecretBoolean", {}),
        (PublicInteger, "PublicInteger", {}),
        (PublicBoolean, "PublicBoolean", {}),
    ],
)
def test_simple_type_conversion(input_type, type_name, kwargs):
    input = create_input(input_type, "name", "party", **kwargs)
    converted_input = to_type_dict(input)
    assert converted_input == type_name


def test_rational_type_conversion():
    input = create_input(SecretRational, "name", "party", digits=3)
    converted_input = to_type_dict(input)
    expected = {"SecretRational": {"digits": 3}}
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
        (operator.add, "Addition", "SecretInteger"),
        (operator.mul, "Multiplication", "SecretInteger"),
        (operator.lt, "LessThan", "SecretBoolean"),
        (operator.gt, "GreaterThan", "SecretBoolean"),
        (operator.le, "LessOrEqualThan", "SecretBoolean"),
        (operator.ge, "GreaterOrEqualThan", "SecretBoolean"),
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
        (operator.add, "Addition", "PublicInteger"),
        (operator.sub, "Subtraction", "PublicInteger"),
        (operator.mul, "Multiplication", "PublicInteger"),
        (operator.truediv, "Division", "PublicInteger"),
        (operator.mod, "Modulo", "PublicInteger"),
        (operator.rshift, "RightShift", "PublicInteger"),
        (operator.lshift, "LeftShift", "PublicInteger"),
        (operator.lt, "LessThan", "PublicBoolean"),
        (operator.gt, "GreaterThan", "PublicBoolean"),
        (operator.le, "LessOrEqualThan", "PublicBoolean"),
        (operator.ge, "GreaterOrEqualThan", "PublicBoolean"),
        (operator.eq, "Equals", "PublicBoolean"),
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
        (operator.add, "Addition", "SecretInteger"),
        (operator.mul, "Multiplication", "SecretInteger"),
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
        (operator.add, "Addition", "SecretInteger"),
        (operator.mul, "Multiplication", "SecretInteger"),        
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


@pytest.mark.parametrize("operator", 
                        [
                            operator.add, 
                            operator.lt,
                            operator.gt,
                            operator.le,
                            operator.ge,
                        ])
def test_rational_digit_checks(operator):
    left = create_input(SecretRational, "left", "party", digits=3)
    right = create_input(SecretRational, "right", "party", digits=4)
    with pytest.raises(Exception):
        operator(left, right)


@pytest.mark.parametrize("operator", [operator.add, operator.lt])
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
        "NadaTuple": {"left_type": "SecretInteger", "right_type": "SecretInteger"}
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
            "left_type": {"Array": {"inner_type": "SecretInteger", "size": 10}},
            "right_type": {"Array": {"inner_type": "SecretInteger", "size": 10}},
        }
    }
