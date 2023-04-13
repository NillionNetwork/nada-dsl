import pytest
import operator

from nada_dsl import *
from nada_dsl.compiler_frontend import (
    nada_dsl_to_nada_mir,
    to_input_list,
    to_type_dict,
    process_operation,
    INPUTS,
    PARTIES
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


def create_output(root: AllTypes, name: str, party: str) -> Output:
    return Output(root, name, Party(party))


def test_root_conversion():
    input = create_input(SecretBigInteger, "input", "input_party")
    output = create_output(input, "output", "output_party")
    mir = nada_dsl_to_nada_mir([output])
    assert len(mir["parties"]) == 2
    assert len(mir["inputs"]) == 1
    assert len(mir["outputs"]) == 1
    assert "source_files" in mir

    mir_output = mir["outputs"][0]
    assert mir_output["name"] == "output"
    assert mir_output["type"] == "SecretBigInteger"
    assert mir_output["party"] == "output_party"
    assert list(mir_output["inner"].keys()) == ["InputReference"]


def test_input_conversion():
    input = Input(name="input", party=Party("party"))
    inputs = {
        "party": {
            "input": (input, "SecretBigInteger")
        }
    }
    converted_inputs = to_input_list(inputs)
    assert len(converted_inputs) == 1

    converted = converted_inputs[0]
    assert converted["name"] == "input"
    assert converted["party"] == "party"
    assert converted["type"] == "SecretBigInteger"


def test_duplicated_inputs_checks():
    party = Party("party")
    left = SecretBigInteger(Input(name="left", party=party))
    right = SecretBigInteger(Input(name="left", party=party))
    new_int = left + right
    output = create_output(new_int, "output", "party")

    with pytest.raises(Exception):
        nada_dsl_to_nada_mir([output])


@pytest.mark.parametrize(
    ("input_type", "type_name", "kwargs"),
    [
        (SecretBigInteger, "SecretBigInteger", {}),
        (SecretString, "SecretString", {"encoding": "Woop"}),
        (SecretBoolean, "SecretBoolean", {}),
    ],
)
def test_simple_type_conversion(input_type, type_name, kwargs):
    input = create_input(input_type, "name", "party", **kwargs)
    converted_input = to_type_dict(input)
    assert converted_input == type_name


def test_fixed_point_rational_type_conversion():
    input = create_input(SecretFixedPointRational, "name", "party", digits=3)
    converted_input = to_type_dict(input)
    expected = {"SecretFixedPointRational": {"digits": 3}}
    assert converted_input == expected


@pytest.mark.parametrize(
    ("operator", "name", "ty"),
    [
        (operator.add, "Addition", "SecretBigInteger"),
        (operator.mul, "Multiplication", "SecretBigInteger"),
        (operator.lt, "CompareLessThan", "SecretBoolean"),
    ],
)
def test_binary_operator(operator, name, ty):
    left = create_input(SecretBigInteger, "left", "party")
    right = create_input(SecretBigInteger, "right", "party")
    program_operation = operator(left, right)
    op = process_operation(program_operation)
    assert list(op.keys()) == [name]

    inner = op[name]

    assert input_reference(inner["left"]) == "left"
    assert input_reference(inner["right"]) == "right"
    assert inner["type"] == ty


@pytest.mark.parametrize("operator", [operator.add, operator.lt])
def test_fixed_point_rational_digit_checks(operator):
    left = create_input(SecretFixedPointRational, "left", "party", digits=3)
    right = create_input(SecretFixedPointRational, "right", "party", digits=4)
    with pytest.raises(Exception):
        operator(left, right)
