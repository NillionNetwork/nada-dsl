"""
Compiler frontend tests.
"""

# pylint: disable=missing-function-docstring

import operator
from typing import Any
import pytest
from betterproto.lib.google.protobuf import Empty

from nada_mir_proto.nillion.nada.operations import v1 as proto_op
from nada_mir_proto.nillion.nada.types import v1 as proto_ty

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    InputASTOperation,
    LiteralASTOperation,
    NadaFunctionASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
    OperationId,
)

# pylint: disable=wildcard-import,unused-wildcard-import
from nada_dsl.nada_types.scalar_types import *
from nada_dsl.program_io import Input, Output
from nada_dsl.compiler_frontend import (
    nada_dsl_to_nada_mir,
    to_input_list,
    process_operation,
    CompilationContext,
)
from nada_dsl.nada_types import AllTypes, Party
from nada_dsl.nada_types.collections import Array, Tuple, NTuple, Object, unzip
from nada_dsl.nada_types.function import NadaFunctionArg
from tests.scalar_type_test import secret_integers


@pytest.fixture(autouse=True)
def clean_inputs():
    AST_OPERATIONS.clear()
    OperationId.reset()
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


def to_mir(name: str):
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
    assert len(mir.parties) == 2
    assert len(mir.inputs) == 1
    assert len(mir.literals) == 0
    assert len(mir.outputs) == 1

    operations = mir.operations
    mir_output = mir.outputs[0]
    assert mir_output.name == "output"
    assert mir_output.type == proto_ty.NadaType(secret_integer=Empty())
    assert mir_output.party == "output_party"

    assert list(filter(lambda op: op.id == mir_output.operation_id, operations))[
        0
    ].operation.input_ref


def test_input_conversion():
    input = Input(name="input", party=Party("party"))
    input.store_in_ast(proto_ty.NadaType(secret_integer=Empty()))
    inputs = {0: AST_OPERATIONS[0]}

    converted_inputs = to_input_list(inputs)
    assert len(converted_inputs) == 1

    converted = converted_inputs[0]
    assert converted.name == "input"
    assert converted.party == "party"
    assert converted.type == proto_ty.NadaType(secret_integer=Empty())


def test_duplicated_inputs_checks():
    party = Party("party")
    left = SecretInteger(Input(name="left", party=party))
    right = SecretInteger(Input(name="left", party=party))
    new_int = left + right
    output = create_output(new_int, "output", "party")

    with pytest.raises(Exception):
        nada_dsl_to_nada_mir([output])


@pytest.mark.parametrize(("input_type", "type_name", "size"), [(Array, "Array", 10)])
def test_array_type_conversion(input_type, type_name, size):
    inner_input = create_input(SecretInteger, "name", "party", **{})
    collection = create_collection(input_type, inner_input, size, **{})
    converted_input = collection.type().to_mir()
    assert converted_input.array


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [
        (Array, "Array"),
    ],
)
def test_zip(input_type, input_name):
    inner_input = create_input(SecretInteger, "left", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})
    inner_input = create_input(SecretInteger, "right", "party", **{})
    right = create_collection(input_type, inner_input, 10, **{})
    zipped = left.zip(right)
    assert isinstance(zipped, Array)
    zip_ast = AST_OPERATIONS[zipped.child.id]
    op = process_operation(zip_ast, CompilationContext())
    assert op.binary.variant == proto_op.BinaryOperationVariant.ZIP

    zip_mir = op

    left = AST_OPERATIONS[op.binary.left]
    right = AST_OPERATIONS[op.binary.right]
    assert left.name == "left"
    assert right.name == "right"
    assert zip_mir.type.array.contained_type.tuple.right == proto_ty.NadaType(
        secret_integer=Empty()
    )
    assert zip_mir.type.array.contained_type.tuple.left == proto_ty.NadaType(
        secret_integer=Empty()
    )


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
    unzip_ast = AST_OPERATIONS[unzipped.child.id]
    assert isinstance(unzip_ast, UnaryASTOperation)
    assert unzip_ast.variant == proto_op.UnaryOperationVariant.UNZIP

    op = process_operation(AST_OPERATIONS[unzipped.child.id], CompilationContext())

    unzip_mir = op
    # Check that the child operation points to a Zip
    zip_ast = AST_OPERATIONS[unzip_mir.unary.this]
    assert isinstance(zip_ast, BinaryASTOperation)
    assert zip_ast.variant == proto_op.BinaryOperationVariant.ZIP
    assert unzip_mir.type.tuple.left == proto_ty.NadaType(
        array=proto_ty.Array(
            contained_type=proto_ty.NadaType(secret_integer=Empty()),
            size=10,
        )
    )
    assert unzip_mir.type.tuple.right == proto_ty.NadaType(
        array=proto_ty.Array(
            contained_type=proto_ty.NadaType(secret_integer=Empty()),
            size=10,
        )
    )


@pytest.mark.parametrize(
    ("input_type", "input_name"),
    [
        (Array, "Array"),
    ],
)
def test_map(input_type, input_name):
    def nada_function(a: SecretInteger) -> SecretInteger:
        return a + a

    inner_input = create_input(SecretInteger, "child", "party", **{})

    left = create_collection(input_type, inner_input, 10, **{})
    map_operation = left.map(nada_function)

    ctx = CompilationContext()
    op = process_operation(AST_OPERATIONS[map_operation.child.id], ctx)
    extra_fn = list(ctx.functions.values())[0]
    assert op.map
    assert op.map.fn == extra_fn.id
    assert op.type.array
    assert op.type.array.contained_type == proto_ty.NadaType(secret_integer=Empty())
    inner_inner = AST_OPERATIONS[op.map.child]
    assert inner_inner.name == "child"


@pytest.mark.parametrize(
    ("input_type"),
    [
        (Array),
    ],
)
def test_reduce(input_type: type[Array]):
    c = create_input(SecretInteger, "c", "party", **{})

    def nada_function(a: SecretInteger, b: SecretInteger) -> SecretInteger:
        return a + b

    inner_input = create_input(SecretInteger, "input", "party", **{})
    left = create_collection(input_type, inner_input, 10, **{})

    reduce_operation = left.reduce(nada_function, c)

    reduce_ast = AST_OPERATIONS[reduce_operation.child.id]
    assert isinstance(reduce_ast, ReduceASTOperation)
    ctx = CompilationContext()
    op = process_operation(reduce_ast, ctx)
    extra_fn = list(ctx.functions.values())[0]

    assert op.reduce
    assert op.reduce.fn == extra_fn.id
    assert op.type == proto_ty.NadaType(secret_integer=Empty())
    inner_inner = AST_OPERATIONS[op.reduce.child]
    assert inner_inner.name == "input"


def check_arg(arg: NadaFunctionArg, arg_name, arg_type):
    assert arg["name"] == arg_name
    assert arg["type"] == arg_type


def check_nada_function_arg_ref(arg_ref, function_id, name, ty):
    assert list(arg_ref.keys()) == ["NadaFunctionArgRef"]
    assert arg_ref["NadaFunctionArgRef"]["function_id"] == function_id
    assert arg_ref["NadaFunctionArgRef"]["refers_to"] == name
    assert arg_ref["NadaFunctionArgRef"]["type"] == ty


def test_array_new():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(SecretInteger, "second", "party", **{})
    array = Array.new(first_input, second_input)

    op = process_operation(AST_OPERATIONS[array.child.id], CompilationContext())

    assert op.new

    first: InputASTOperation = AST_OPERATIONS[op.new.elements[0]]  # type: ignore
    second: InputASTOperation = AST_OPERATIONS[op.new.elements[1]]  # type: ignore

    assert first.name == "first"
    assert second.name == "second"
    assert op.type.array.contained_type == proto_ty.NadaType(secret_integer=Empty())
    assert op.type.array.size == 2


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
    tuple = Tuple.new(first_input, second_input)
    array_ast = AST_OPERATIONS[tuple.child.id]

    op = process_operation(array_ast, CompilationContext())

    assert op.new

    left_ast = AST_OPERATIONS[op.new.elements[0]]
    right_ast = AST_OPERATIONS[op.new.elements[1]]
    assert left_ast.name == "first"
    assert right_ast.name == "second"
    assert op.type.tuple.left == proto_ty.NadaType(secret_integer=Empty())
    assert op.type.tuple.right == proto_ty.NadaType(integer=Empty())


def test_tuple_new_empty():
    with pytest.raises(TypeError) as e:
        Tuple.new()
    assert (
        str(e.value)
        == "Tuple.new() missing 2 required positional arguments: 'left_value' and 'right_value'"
    )


def test_n_tuple_new():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(PublicInteger, "second", "party", **{})
    third_input = create_input(SecretInteger, "third", "party", **{})
    tuple = NTuple.new([first_input, second_input, third_input])
    array_ast = AST_OPERATIONS[tuple.child.id]

    op = process_operation(array_ast, CompilationContext())

    assert op.new

    first_ast = AST_OPERATIONS[op.new.elements[0]]
    second_ast = AST_OPERATIONS[op.new.elements[1]]
    third_ast = AST_OPERATIONS[op.new.elements[2]]
    assert first_ast.name == "first"
    assert second_ast.name == "second"
    assert third_ast.name == "third"
    assert op.type.ntuple.fields == [
        proto_ty.NadaType(secret_integer=Empty()),
        proto_ty.NadaType(integer=Empty()),
        proto_ty.NadaType(secret_integer=Empty()),
    ]


def test_object_new():
    first_input = create_input(SecretInteger, "first", "party", **{})
    second_input = create_input(PublicInteger, "second", "party", **{})
    third_input = create_input(SecretInteger, "third", "party", **{})
    object = Object.new({"a": first_input, "b": second_input, "c": third_input})
    array_ast = AST_OPERATIONS[object.child.id]

    op = process_operation(array_ast, CompilationContext())

    assert op.new

    first_ast = AST_OPERATIONS[op.new.elements[0]]
    second_ast = AST_OPERATIONS[op.new.elements[1]]
    third_ast = AST_OPERATIONS[op.new.elements[2]]
    assert first_ast.name == "first"
    assert second_ast.name == "second"
    assert third_ast.name == "third"

    assert op.type.object.fields == [
        proto_ty.ObjectEntry(name="a", type=proto_ty.NadaType(secret_integer=Empty())),
        proto_ty.ObjectEntry(name="b", type=proto_ty.NadaType(integer=Empty())),
        proto_ty.ObjectEntry(name="c", type=proto_ty.NadaType(secret_integer=Empty())),
    ]


@pytest.mark.parametrize(
    ("binary_operator", "ty"),
    [
        (operator.add, proto_ty.NadaType(integer=Empty())),
        (operator.sub, proto_ty.NadaType(integer=Empty())),
        (operator.mul, proto_ty.NadaType(integer=Empty())),
        (operator.truediv, proto_ty.NadaType(integer=Empty())),
        (operator.mod, proto_ty.NadaType(integer=Empty())),
        (operator.pow, proto_ty.NadaType(integer=Empty())),
        (operator.lt, proto_ty.NadaType(boolean=Empty())),
        (operator.gt, proto_ty.NadaType(boolean=Empty())),
        (operator.le, proto_ty.NadaType(boolean=Empty())),
        (operator.ge, proto_ty.NadaType(boolean=Empty())),
        (operator.eq, proto_ty.NadaType(boolean=Empty())),
    ],
)
def test_binary_operator_integer_integer(binary_operator, ty):
    left = create_literal(Integer, -2)
    right = create_literal(Integer, -2)
    program_operation = binary_operator(left, right)
    # recover operation from AST
    ast_operation = AST_OPERATIONS[program_operation.child.id]
    op = process_operation(ast_operation, CompilationContext())
    assert op.literal_ref
    assert op.type == ty


@pytest.mark.parametrize(
    ("operator", "variant", "ty"),
    [
        (
            operator.add,
            proto_op.BinaryOperationVariant.ADDITION,
            proto_ty.NadaType(integer=Empty()),
        ),
        (
            operator.sub,
            proto_op.BinaryOperationVariant.SUBTRACTION,
            proto_ty.NadaType(integer=Empty()),
        ),
        (
            operator.mul,
            proto_op.BinaryOperationVariant.MULTIPLICATION,
            proto_ty.NadaType(integer=Empty()),
        ),
        (
            operator.truediv,
            proto_op.BinaryOperationVariant.DIVISION,
            proto_ty.NadaType(integer=Empty()),
        ),
        (
            operator.mod,
            proto_op.BinaryOperationVariant.MODULO,
            proto_ty.NadaType(integer=Empty()),
        ),
        (
            operator.pow,
            proto_op.BinaryOperationVariant.POWER,
            proto_ty.NadaType(integer=Empty()),
        ),
        (
            operator.lt,
            proto_op.BinaryOperationVariant.LESS_THAN,
            proto_ty.NadaType(boolean=Empty()),
        ),
        (
            operator.gt,
            proto_op.BinaryOperationVariant.GREATER_THAN,
            proto_ty.NadaType(boolean=Empty()),
        ),
        (
            operator.le,
            proto_op.BinaryOperationVariant.LESS_EQ,
            proto_ty.NadaType(boolean=Empty()),
        ),
        (
            operator.ge,
            proto_op.BinaryOperationVariant.GREATER_EQ,
            proto_ty.NadaType(boolean=Empty()),
        ),
        (
            operator.eq,
            proto_op.BinaryOperationVariant.EQUALS,
            proto_ty.NadaType(boolean=Empty()),
        ),
    ],
)
def test_binary_operator_integer_publicinteger(operator, variant, ty):
    left = create_literal(Integer, -3)
    right = create_input(PublicInteger, "right", "party")
    program_operation = operator(left, right)
    # recover operation from AST
    ast_operation = AST_OPERATIONS[program_operation.child.id]
    op = process_operation(ast_operation, CompilationContext())
    assert op.binary.variant == variant

    left_ast = AST_OPERATIONS[op.binary.left]
    right_ast = AST_OPERATIONS[op.binary.right]
    assert isinstance(left_ast, LiteralASTOperation)
    assert left_ast.value == -3
    assert isinstance(right_ast, InputASTOperation)
    assert right_ast.name == "right"
    assert op.type == ty


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
    ast = AST_OPERATIONS[operation.child.id]
    op = process_operation(ast, CompilationContext())
    assert op.unary.variant == proto_op.UnaryOperationVariant.NOT

    bool1 = PublicBoolean(Input(name="my_bool_1", party=party1))
    operation = ~bool1
    ast = AST_OPERATIONS[operation.child.id]
    op = process_operation(ast, CompilationContext())
    assert op.unary.variant == proto_op.UnaryOperationVariant.NOT

    bool1 = Boolean(True)
    bool2 = ~bool1
    assert bool2 == Boolean(False)
