"""
Compiler frontend tests.
"""

# pylint: disable=missing-function-docstring

import operator
from typing import Any
import pytest
from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    InputASTOperation,
    LiteralASTOperation,
    NadaFunctionASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
)

# pylint: disable=wildcard-import,unused-wildcard-import
from nada_dsl.nada_types.scalar_types import *
from nada_dsl.program_io import Input, Output
from nada_dsl.compiler_frontend import (
    nada_dsl_to_nada_mir,
    to_input_list,
    process_operation,
    INPUTS,
    PARTIES,
    FUNCTIONS,
    traverse_and_process_operations,
)
from nada_dsl.nada_types import AllTypes, Party
from nada_dsl.nada_types.collections import Array, Vector, Tuple, unzip
from nada_dsl.nada_types.function import NadaFunctionArg, NadaFunctionCall, nada_fn


@pytest.fixture(autouse=True)
def clean_inputs():
    PARTIES.clear()
    INPUTS.clear()
    FUNCTIONS.clear()
    AST_OPERATIONS.clear()
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

    operations = mir["operations"]
    mir_output = mir["outputs"][0]
    assert mir_output["name"] == "output"
    assert mir_output["type"] == "SecretInteger"
    assert mir_output["party"] == "output_party"

    assert list(operations[mir_output["operation_id"]].keys()) == ["InputReference"]


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
    collection = create_collection(input_type, inner_input, size, **{})
    converted_input = collection.to_type()
    assert list(converted_input.keys()) == [type_name]


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [
        (Array, "Array"),
        # TODO(Vector, "Vector")
    ],
)
def test_zip(input_type, input_name):
    inner_input = create_input(SecretInteger, "left", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    inner_input = create_input(SecretInteger, "right", "party", **{})
    right = create_collection(input_type, inner_input, 10, **{})
    zipped = left.zip(right)
    assert isinstance(zipped, Array)
    zip_ast = AST_OPERATIONS[zipped.inner.id]
    op = process_operation(zip_ast, {}).mir
    assert list(op.keys()) == ["Zip"]

    zip_mir = op["Zip"]

    left = AST_OPERATIONS[zip_mir["left"]]
    right = AST_OPERATIONS[zip_mir["right"]]
    assert left.name == "left"
    assert right.name == "right"
    assert zip_mir["type"][input_name]["inner_type"] == {
        "Tuple": {
            "left_type": "SecretInteger",
            "right_type": "SecretInteger",
        }
    }


@pytest.mark.parametrize(
    ("input_type"),
    [(Array)],
)
def test_unzip(input_type: type[Array]):
    inner_input = create_input(SecretInteger, "left", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    inner_input = create_input(SecretInteger, "right", "party", **{})
    right = create_collection(input_type, inner_input, 10, **{})
    unzipped = unzip(left.zip(right))
    assert isinstance(unzipped, Tuple)
    unzip_ast = AST_OPERATIONS[unzipped.inner.id]
    assert isinstance(unzip_ast, UnaryASTOperation)
    assert unzip_ast.name == "Unzip"

    op = process_operation(AST_OPERATIONS[unzipped.inner.id], {}).mir

    unzip_mir = op["Unzip"]
    # Check that the inner operation points to a Zip
    zip_ast = AST_OPERATIONS[unzip_mir["this"]]
    assert isinstance(zip_ast, BinaryASTOperation)
    assert zip_ast.name == "Zip"
    assert unzip_mir["type"] == {
        "Tuple": {
            "left_type": {"Array": {"inner_type": "SecretInteger", "size": 10}},
            "right_type": {"Array": {"inner_type": "SecretInteger", "size": 10}},
        }
    }


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [
        (Array, "Array"),  # TODO (Vector, "Vector")
    ],
)
def test_map(input_type, input_name):
    @nada_fn
    def nada_function(a: SecretInteger) -> SecretInteger:
        return a + a

    inner_input = create_input(SecretInteger, "inner", "party", **{})

    left = create_collection(input_type, inner_input, 10, **{})
    map_operation = left.map(nada_function)

    process_output = process_operation(AST_OPERATIONS[map_operation.inner.id], {})
    op = process_output.mir
    extra_fn = process_output.extra_function
    assert list(op.keys()) == ["Map"]
    inner = op["Map"]
    assert inner["fn"] == extra_fn.id
    assert list(inner["type"].keys()) == [input_name]
    inner_inner = AST_OPERATIONS[inner["inner"]]
    assert inner_inner.name == "inner"
    assert inner["type"][input_name]["inner_type"] == "SecretInteger"


@pytest.mark.parametrize(
    ("input_type"),
    [
        (Array),  # TODO (Vector, "Vector")
    ],
)
def test_reduce(input_type: type[Array]):
    c = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    inner_input = create_input(SecretInteger, "inner", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})

    reduce_operation = left.reduce(nada_function, c)

    reduce_ast = AST_OPERATIONS[reduce_operation.inner.id]
    assert isinstance(reduce_ast, ReduceASTOperation)
    process_output = process_operation(reduce_ast, {})
    op = process_output.mir
    extra_fn = process_output.extra_function

    assert list(op.keys()) == ["Reduce"]
    inner = op["Reduce"]
    assert inner["fn"] == extra_fn.id
    assert inner["type"] == "SecretInteger"
    inner_inner = AST_OPERATIONS[inner["inner"]]
    assert inner_inner.name == "inner"


def check_arg(arg: NadaFunctionArg, arg_name, arg_type):
    assert arg["name"] == arg_name
    assert arg["type"] == arg_type


def check_nada_function_arg_ref(arg_ref, function_id, name, ty):
    assert list(arg_ref.keys()) == ["NadaFunctionArgRef"]
    assert arg_ref["NadaFunctionArgRef"]["function_id"] == function_id
    assert arg_ref["NadaFunctionArgRef"]["refers_to"] == name
    assert arg_ref["NadaFunctionArgRef"]["type"] == ty


def nada_function_to_mir(function_name: str):
    nada_function: NadaFunctionASTOperation = find_function_in_ast(function_name)
    assert isinstance(nada_function, NadaFunctionASTOperation)
    fn_ops = {}
    traverse_and_process_operations(nada_function.inner, fn_ops, {})
    return nada_function.to_mir(fn_ops)


def test_nada_function_simple():
    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    nada_function = nada_function_to_mir("nada_function")
    assert nada_function["function"] == "nada_function"
    args = nada_function["args"]
    assert len(args) == 2
    check_arg(args[0], "a", "SecretInteger")
    check_arg(args[1], "b", "SecretInteger")
    assert nada_function["return_type"] == "SecretInteger"

    operations = nada_function["operations"]
    return_op = operations[nada_function["return_operation_id"]]
    assert list(return_op.keys()) == ["Addition"]
    addition = return_op["Addition"]

    check_nada_function_arg_ref(
        operations[addition["left"]], nada_function["id"], "a", "SecretInteger"
    )
    check_nada_function_arg_ref(
        operations[addition["right"]], nada_function["id"], "b", "SecretInteger"
    )


def test_nada_function_using_inputs():
    c = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b + c

    nada_function = nada_function_to_mir("nada_function")
    assert nada_function["function"] == "nada_function"
    args = nada_function["args"]
    assert len(args) == 2
    check_arg(args[0], "a", "SecretInteger")
    check_arg(args[1], "b", "SecretInteger")
    assert nada_function["return_type"] == "SecretInteger"

    operation = nada_function["operations"]
    return_op = operation[nada_function["return_operation_id"]]

    assert list(return_op.keys()) == ["Addition"]
    addition = return_op["Addition"]
    addition_right = operation[addition["right"]]
    assert input_reference(addition_right) == "c"
    addition_left = operation[addition["left"]]
    assert list(addition_left.keys()) == ["Addition"]

    addition = addition_left["Addition"]

    check_nada_function_arg_ref(
        operation[addition["left"]], nada_function["id"], "a", "SecretInteger"
    )
    check_nada_function_arg_ref(
        operation[addition["right"]], nada_function["id"], "b", "SecretInteger"
    )


def test_nada_function_call():

    c = create_input(SecretInteger, "c", "party", **{})
    d = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    nada_fn_call_return = nada_function(c, d)
    nada_fn_type = nada_function_to_mir("nada_function")

    nada_function_call = nada_fn_call_return.inner
    assert isinstance(nada_function_call, NadaFunctionCall)
    assert nada_function_call.fn.id == nada_fn_type["id"]


def test_nada_function_using_operations():

    c = create_input(SecretInteger, "c", "party", **{})
    d = create_input(SecretInteger, "d", "party", **{})

    @nada_fn
    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b + c + d

    nada_function_ast = nada_function_to_mir("nada_function")
    assert nada_function_ast["function"] == "nada_function"
    args = nada_function_ast["args"]
    assert len(args) == 2
    check_arg(args[0], "a", "SecretInteger")
    check_arg(args[1], "b", "SecretInteger")
    assert nada_function_ast["return_type"] == "SecretInteger"

    operation = nada_function_ast["operations"]
    return_op = operation[nada_function_ast["return_operation_id"]]

    assert list(return_op.keys()) == ["Addition"]
    addition = return_op["Addition"]

    assert input_reference(operation[addition["right"]]) == "d"
    addition_left = operation[addition["left"]]
    assert list(addition_left.keys()) == ["Addition"]
    addition = addition_left["Addition"]
    assert input_reference(operation[addition["right"]]) == "c"

    addition_left = operation[addition["left"]]
    assert list(addition_left.keys()) == ["Addition"]
    addition = addition_left["Addition"]

    check_nada_function_arg_ref(
        operation[addition["left"]], nada_function_ast["id"], "a", "SecretInteger"
    )
    check_nada_function_arg_ref(
        operation[addition["right"]], nada_function_ast["id"], "b", "SecretInteger"
    )


def find_function_in_ast(fn_name: str):
    for op in AST_OPERATIONS.values():
        if isinstance(op, NadaFunctionASTOperation) and op.name == fn_name:
            return op
    return None


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [
        (Array, "Array"),  # TODO(Vector, "Vector")
    ],
)
def test_nada_function_using_matrix(input_type, input_name):
    c = create_input(SecretInteger, "c", "party", **{})

    @nada_fn
    def add(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    @nada_fn
    def matrix_addition(
        a: input_type[SecretInteger], b: input_type[SecretInteger]
    ) -> SecretInteger:
        return a.zip(b).map(add).reduce(add, c)

    add_fn = nada_function_to_mir("add")
    matrix_addition_fn = nada_function_to_mir("matrix_addition")
    assert matrix_addition_fn["function"] == "matrix_addition"
    args = matrix_addition_fn["args"]
    assert len(args) == 2
    a_arg_type = {input_name: {"inner_type": "SecretInteger"}}
    check_arg(args[0], "a", a_arg_type)
    b_arg_type = {input_name: {"inner_type": "SecretInteger"}}
    check_arg(args[1], "b", b_arg_type)
    assert matrix_addition_fn["return_type"] == "SecretInteger"

    operations = matrix_addition_fn["operations"]
    return_op = operations[matrix_addition_fn["return_operation_id"]]
    assert list(return_op.keys()) == ["Reduce"]
    reduce_op = return_op["Reduce"]
    reduce_op["function_id"] = add_fn["id"]
    reduce_op["type"] = "SecretInteger"

    reduce_op_inner = operations[reduce_op["inner"]]
    assert list(reduce_op_inner.keys()) == ["Map"]
    map_op = reduce_op_inner["Map"]
    map_op["function_id"] = add_fn["id"]
    map_op["type"] = {input_name: {"inner_type": "SecretInteger", "size": None}}

    map_op_inner = operations[map_op["inner"]]
    assert list(map_op_inner.keys()) == ["Zip"]
    zip_op = map_op_inner["Zip"]

    zip_op_left = operations[zip_op["left"]]
    zip_op_right = operations[zip_op["right"]]
    check_nada_function_arg_ref(zip_op_left, matrix_addition_fn["id"], "a", a_arg_type)
    check_nada_function_arg_ref(zip_op_right, matrix_addition_fn["id"], "b", b_arg_type)


def test_array_new():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(SecretInteger, "second", "party", **{})
    array = Array.new(first_input, second_input)

    op = process_operation(AST_OPERATIONS[array.inner.id], {}).mir

    assert list(op.keys()) == ["New"]

    inner = op["New"]

    first: InputASTOperation = AST_OPERATIONS[inner["elements"][0]]  # type: ignore
    second: InputASTOperation = AST_OPERATIONS[inner["elements"][1]]  # type: ignore

    assert first.name == "first"
    assert second.name == "second"
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
    array_ast = AST_OPERATIONS[array.inner.id]

    op = process_operation(array_ast, {}).mir

    assert list(op.keys()) == ["New"]

    inner = op["New"]

    left_ast = AST_OPERATIONS[inner["elements"][0]]
    right_ast = AST_OPERATIONS[inner["elements"][1]]
    assert left_ast.name == "first"
    assert right_ast.name == "second"
    assert inner["type"]["Tuple"] == {
        "left_type": "SecretInteger",
        "right_type": "Integer",
    }


def test_tuple_new_empty():
    with pytest.raises(TypeError) as e:
        Tuple.new()
    assert (
        str(e.value)
        == "Tuple.new() missing 2 required positional arguments: 'left_type' and 'right_type'"
    )


@pytest.mark.parametrize(
    ("binary_operator", "name", "ty"),
    [
        (operator.add, "LiteralReference", "Integer"),
        (operator.sub, "LiteralReference", "Integer"),
        (operator.mul, "LiteralReference", "Integer"),
        (operator.truediv, "LiteralReference", "Integer"),
        (operator.mod, "LiteralReference", "Integer"),
        (operator.pow, "LiteralReference", "Integer"),
        (operator.lt, "LiteralReference", "Boolean"),
        (operator.gt, "LiteralReference", "Boolean"),
        (operator.le, "LiteralReference", "Boolean"),
        (operator.ge, "LiteralReference", "Boolean"),
        (operator.eq, "LiteralReference", "Boolean"),
    ],
)
def test_binary_operator_integer_integer(binary_operator, name, ty):
    left = create_literal(Integer, -2)
    right = create_literal(Integer, -2)
    program_operation = binary_operator(left, right)
    # recover operation from AST
    ast_operation = AST_OPERATIONS[program_operation.inner.id]
    op = process_operation(ast_operation, {}).mir
    assert list(op.keys()) == [name]
    inner = op[name]
    assert inner["type"] == to_type(ty)


@pytest.mark.parametrize(
    ("operator", "name", "ty"),
    [
        (operator.add, "Addition", "PublicInteger"),
        (operator.sub, "Subtraction", "PublicInteger"),
        (operator.mul, "Multiplication", "PublicInteger"),
        (operator.truediv, "Division", "PublicInteger"),
        (operator.mod, "Modulo", "PublicInteger"),
        (operator.pow, "Power", "PublicInteger"),
        (operator.lt, "LessThan", "PublicBoolean"),
        (operator.gt, "GreaterThan", "PublicBoolean"),
        (operator.le, "LessOrEqualThan", "PublicBoolean"),
        (operator.ge, "GreaterOrEqualThan", "PublicBoolean"),
        (operator.eq, "Equals", "PublicBoolean"),
    ],
)
def test_binary_operator_integer_publicinteger(operator, name, ty):
    left = create_literal(Integer, -3)
    right = create_input(PublicInteger, "right", "party")
    program_operation = operator(left, right)
    # recover operation from AST
    ast_operation = AST_OPERATIONS[program_operation.inner.id]
    op = process_operation(ast_operation, {}).mir
    assert list(op.keys()) == [name]
    inner = op[name]
    left_ast = AST_OPERATIONS[inner["left"]]
    right_ast = AST_OPERATIONS[inner["right"]]
    assert isinstance(left_ast, LiteralASTOperation)
    assert left_ast.value == -3
    assert isinstance(right_ast, InputASTOperation)
    assert right_ast.name == "right"
    assert inner["type"] == to_type(ty)


def test_logical_operations():
    party1 = Party(name="Party1")
    int1 = SecretInteger(Input(name="my_int_1", party=party1))
    int2 = SecretInteger(Input(name="my_int_2", party=party1))
    with pytest.raises(NotImplementedError):
        int1 or int2
    with pytest.raises(NotImplementedError):
        int1 and int2
    with pytest.raises(NotImplementedError):
        not int1

def test_logical_operations_with_secret_boolean():
    party1 = Party(name="Party1")
    bool1 = SecretBoolean(Input(name="my_bool_1", party=party1))
    bool2 = SecretBoolean(Input(name="my_bool_2", party=party1))
    with pytest.raises(NotImplementedError):
        bool1 or bool2
    with pytest.raises(NotImplementedError):
        bool1 and bool2
    with pytest.raises(NotImplementedError):
        not bool1

def test_not():
    party1 = Party(name="Party1")
    bool1 = SecretBoolean(Input(name="my_bool_1", party=party1))
    operation = ~bool1
    ast = AST_OPERATIONS[operation.inner.id]
    op = process_operation(ast, {}).mir
    assert list(op.keys()) == ["Not"]

    bool1 = PublicBoolean(Input(name="my_bool_1", party=party1))
    operation = ~bool1
    ast = AST_OPERATIONS[operation.inner.id]
    op = process_operation(ast, {}).mir
    assert list(op.keys()) == ["Not"]

    bool1 = Boolean(True)
    bool2 = ~bool1
    assert bool2 == Boolean(False)