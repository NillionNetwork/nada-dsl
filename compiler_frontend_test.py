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
from addition_fixed_point_rational import nada_main as addition_fixed_point_rational
from addition_fixed_point_rational_error import (
    nada_main as addition_fixed_point_rational_error,
)
from addition_simple import nada_main as addition_simple
from circuit_simple import nada_main as circuit_simple
from circuit_simple_2 import nada_main as circuit_simple_2
from fixed_point_rational import nada_main as fixed_point_rational
from import_file import nada_main as import_file
from input_single import nada_main as input_single
from integer import nada_main as integer
from multiplication_fixed_point_rational import (
    nada_main as multiplication_fixed_point_rational,
)
from multiplication_simple import nada_main as multiplication_simple
from secret_string import nada_main as secret_string

mir_files_directory = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), f"../tests/resources/mir/"
)

testdata = [
    (addition_fixed_point_rational, "addition_fixed_point_rational"),
    (addition_simple, "addition_simple"),
    (circuit_simple, "circuit_simple"),
    (circuit_simple_2, "circuit_simple_2"),
    (fixed_point_rational, "fixed_point_rational"),
    (import_file, "import_file"),
    (input_single, "input_single"),
    (integer, "integer"),
    (
        multiplication_fixed_point_rational,
        "multiplication_fixed_point_rational",
    ),
    (multiplication_simple, "multiplication_simple"),
    (secret_string, "secret_string"),
]

test_ids = [
    "addition_fixed_point_rational",
    "addition_simple",
    "circuit_simple",
    "circuit_simple_2",
    "fixed_point_rational",
    "import_file",
    "input_single",
    "integer",
    "multiplication_fixed_point_rational",
    "multiplication_simple",
    "secret_string",
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
    addition_fixed_point_rational_error,
]

error_test_ids = [
    "addition_fixed_point_rational_error",
]


@pytest.mark.parametrize("outputs", error_testdata, ids=error_test_ids)
def test_error_in_compile_to_nada_mir(outputs):
    with pytest.raises(Exception):
        nada_dsl_to_nada_mir(outputs())
