import os
import sys
import json
import pytest

from deepdiff import DeepDiff
from nada_dsl.compiler_frontend import nada_dsl_to_nada_mir

tests_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), f"../tests/resources/programs/current/"
)

sys.path.insert(0, tests_directory)
from addition_fixed_float_point import outputs as addition_fixed_float_point
from addition_fixed_float_point_error import outputs as addition_fixed_float_point_error
from addition_simple import outputs as addition_simple
from circuit_simple import outputs as circuit_simple
from circuit_simple_2 import outputs as circuit_simple_2
from fixed_float_point import outputs as fixed_float_point
from import_file import outputs as import_file
from input_single import outputs as input_single
from integer import outputs as integer
from multiplication_fixed_float_point import outputs as multiplication_fixed_float_point
from multiplication_fixed_float_point_error import (
    outputs as multiplication_fixed_float_point_error,
)
from multiplication_simple import outputs as multiplication_simple

mir_files_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), f"../tests/resources/mir/"
)

testdata = [
    (addition_fixed_float_point, "current.addition_fixed_float_point"),
    (addition_simple, "current.addition_simple"),
    (circuit_simple, "current.circuit_simple"),
    (circuit_simple_2, "current.circuit_simple_2"),
    (fixed_float_point, "current.fixed_float_point"),
    (import_file, "current.import_file"),
    (input_single, "current.input_single"),
    (integer, "current.integer"),
    (multiplication_fixed_float_point, "current.multiplication_fixed_float_point"),
    (multiplication_simple, "current.multiplication_simple"),
]

test_ids = [
    "addition_fixed_float_point",
    "addition_simple",
    "circuit_simple",
    "circuit_simple_2",
    "fixed_float_point",
    "import_file",
    "input_single",
    "integer",
    "multiplication_fixed_float_point",
    "multiplication_simple",
]


@pytest.mark.parametrize(("outputs", "expected_file_name"), testdata, ids=test_ids)
def test_compile_to_nada_mir(outputs, expected_file_name):
    mir_model = nada_dsl_to_nada_mir(outputs())

    file = open(f"{mir_files_directory}{expected_file_name}.nada-mir.json")
    expected_mir_model = json.load(file)

    assert not DeepDiff(
        mir_model, expected_mir_model, exclude_paths="root['source_files']"
    ).pretty()


error_testdata = [
    addition_fixed_float_point_error,
    multiplication_fixed_float_point_error,
]

error_test_ids = [
    "addition_fixed_float_point_error",
    "multiplication_fixed_float_point_error",
]


@pytest.mark.parametrize("outputs", error_testdata, ids=error_test_ids)
def test_error_in_compile_to_nada_mir(outputs):
    with pytest.raises(Exception):
        nada_dsl_to_nada_mir(outputs())
