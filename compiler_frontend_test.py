import os
import sys
import json
import pytest

from deepdiff import DeepDiff
from nada_dsl.compiler_frontend import nada_dsl_to_nada_mir

tests_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"../tests/resources/circuits/current/")

sys.path.insert(0, tests_directory)
from addition_simple import outputs as addition_simple
from circuit_simple import outputs as circuit_simple
from circuit_simple_2 import outputs as circuit_simple_2
from empty import outputs as empty
from input_single import outputs as input_single
from integer import outputs as integer
from multiplication_simple import outputs as multiplication_simple
from output_multiple import outputs as output_multiple
from import_file import outputs as import_file

mir_files_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"../tests/resources/mir/")

testdata = [
    (addition_simple, 'current.addition_simple'),
    (circuit_simple, 'current.circuit_simple'),
    (circuit_simple_2, 'current.circuit_simple_2'),
    (empty, 'current.empty'),
    (input_single, 'current.input_single'),
    (integer, 'current.integer'),
    (multiplication_simple, 'current.multiplication_simple'),
    (output_multiple, 'current.output_multiple'),
    (import_file, 'current.import_file'),
]

test_ids = [
    'addition_simple',
    'circuit_simple',
    'circuit_simple_2',
    'empty',
    'input_single',
    'integer',
    'multiplication_simple',
    'output_multiple',
    'import_file',
]


@pytest.mark.parametrize(('outputs', 'expected_file_name'), testdata, ids=test_ids)
def test_compile_to_nada_mir(outputs, expected_file_name):
    mir_model = nada_dsl_to_nada_mir(outputs())

    file = open(f"{mir_files_directory}{expected_file_name}.nada-mir.json")
    expected_mir_model = json.load(file)

    assert not DeepDiff(mir_model, expected_mir_model, view="tree", exclude_regex_paths="['source_ref']")

