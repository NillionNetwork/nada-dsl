"""
Compilation tests.
"""
import os
import json
from nada_dsl.compile import transform_program

def get_test_programs_folder():
    file_path = os.path.realpath(__file__)
    this_directory = os.path.dirname(file_path)
    return this_directory+'/../../test-programs/programs'


def test_compile_nada_fn_simple():
    mir_str = transform_program(f'{get_test_programs_folder()}/nada_fn_simple.py').mir
    assert mir_str != ""
    mir = json.loads(mir_str)
    mir_functions = mir['functions']
    assert len(mir_functions) == 1
