import json
import os
from json import JSONEncoder
import inspect
from typing import List, Optional, Dict, Any

from nada_dsl.source_ref import SourceRef
from nada_dsl.circuit_io import Input, Output
from nada_dsl.nada_types.rational import SecretFixedPointRational
from nada_dsl.nada_types.string import SecretString
from nada_dsl.nada_types.collections import (
    Array,
    Vector,
    NadaTuple,
    ArrayType,
    VectorType,
    NadaTupleType,
)
from nada_dsl.nada_types.function import NadaFunction
from nada_dsl.operations import Map, Reduce, Zip, Unzip
from nada_dsl.future.operations import Cast
from nada_dsl.operations import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Modulo,
    RightShift,
    LeftShift,
    LessThan,
    GreaterThan,
    LessOrEqualThan,
    GreaterOrEqualThan,
    Equals,
)

INPUTS = {}
PARTIES = {}
FUNCTIONS = {}


class ClassEncoder(JSONEncoder):
    def default(self, o):
        if inspect.isclass(o):
            return o.__name__
        return {type(o).__name__: o.__dict__}


def get_target_dir() -> str:
    env_dir = os.environ.get("NADA_TARGET_DIR")
    if env_dir:
        return env_dir

    cwd = os.getcwd()

    try:
        os.mkdir("target")
    except FileExistsError:
        pass

    return os.path.join(cwd, "target")


def nada_compile(outputs: List[Output]) -> str:
    compiled = nada_dsl_to_nada_mir(outputs)
    return json.dumps(compiled)


def compile_to_nada_pydsl_hir(output_file, outputs, target_dir):
    nada_pydsl_hir = json.dumps(outputs, cls=ClassEncoder, indent=2)
    with open(f"{target_dir}/{output_file}.nada-pydsl-hir.json", "w") as file:
        file.write(nada_pydsl_hir)


def compile_to_nada_mir(target_dir, outputs, output_file):
    circuit = nada_dsl_to_nada_mir(outputs)
    nada_mir = json.dumps(circuit, indent=2)
    with open(f"{target_dir}/{output_file}.nada-mir.json", "w") as file:
        file.write(nada_mir)


def nada_dsl_to_nada_mir(outputs: List[Output]) -> Dict[str, Any]:
    new_outputs = []
    PARTIES.clear()
    INPUTS.clear()
    for output in outputs:
        new_out = process_operation(output.inner)
        party = output.party
        PARTIES[party.name] = party
        new_outputs.append(
            {
                "inner": new_out,
                "name": output.name,
                "party": party.name,
                "type": to_type_dict(output.inner),
                "source_ref": output.source_ref.to_dict(),
            }
        )

    return {
        "functions": to_function_list(FUNCTIONS),
        "parties": to_party_list(PARTIES),
        "inputs": to_input_list(INPUTS),
        "outputs": new_outputs,
        "source_files": SourceRef.get_sources(),
    }


def to_party_list(parties):
    return [
        {
            "name": party.name,
            "source_ref": party.source_ref.to_dict(),
        }
        for party in parties.values()
    ]


def to_input_list(inputs):
    input_list = []
    for party_inputs in inputs.values():
        for program_input, program_type in party_inputs.values():
            input_list.append(
                {
                    "name": program_input.name,
                    "type": program_type,
                    "party": program_input.party.name,
                    "doc": program_input.doc,
                    "source_ref": program_input.source_ref.to_dict(),
                }
            )
    return input_list


def to_function_list(functions):
    function_list = []
    for function in functions.values():
        function_list.append(to_fn_dict(function))
    return function_list

def to_type_dict(op_wrapper):
    if type(op_wrapper) == Array or type(op_wrapper) == ArrayType:
        return {
            "Array": {
                "size": op_wrapper.size,
                "inner_type": to_type_dict(op_wrapper.inner_type),
            }
        }
    elif type(op_wrapper) == Vector or type(op_wrapper) == VectorType:
        return {"Vector": {"inner_type": to_type_dict(op_wrapper.inner_type)}}
    elif type(op_wrapper) == NadaTuple or type(op_wrapper) == NadaTupleType:
        return {
            "NadaTuple": {
                "left_type": to_type_dict(op_wrapper.left_type),
                "right_type": to_type_dict(op_wrapper.right_type),
            }
        }
    elif type(op_wrapper) == SecretString:
        return {
            "SecretString": {
                "length": op_wrapper.length,
            }
        }
    elif type(op_wrapper) == SecretFixedPointRational:
        return {
            "SecretFixedPointRational": {
                "digits": op_wrapper.digits,
            }
        }
    elif inspect.isclass(op_wrapper):
        return op_wrapper.__name__
    else:
        return op_wrapper.__class__.__name__


def to_fn_dict(fn: NadaFunction):
    return {
        "id": fn.id,
        "args": [{"name": arg.name, "type": arg.type.__name__} for arg in fn.args],
        "function": fn.function.__name__,
        "inner": process_operation(fn.inner),
        "return_type": fn.return_type.__name__,
    }


def process_operation(operation_wrapper):
    from nada_dsl.nada_types.function import NadaFunctionArg

    ty = to_type_dict(operation_wrapper)
    operation = operation_wrapper.inner

    if type(operation) == Addition:
        return {
            "Addition": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Subtraction:
        return {
            "Subtraction": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Multiplication:
        return {
            "Multiplication": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Division:
        return {
            "Division": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Modulo:
        return {
            "Modulo": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == RightShift:
        return {
            "RightShift": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == LeftShift:
        return {
            "LeftShift": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == LessThan:
        return {
            "LessThan": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == GreaterThan:
        return {
            "GreaterThan": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == LessOrEqualThan:
        return {
            "LessOrEqualThan": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == GreaterOrEqualThan:
        return {
            "GreaterOrEqualThan": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Equals:
        return {
            "Equals": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Cast:
        return {
            "Cast": {
                "target": process_operation(operation.target),
                "to": operation.to.__name__,
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Input:
        party_name = operation.party.name
        PARTIES[party_name] = operation.party
        if party_name not in INPUTS:
            INPUTS[party_name] = {}
        if operation.name in INPUTS[party_name] and id(
            INPUTS[party_name][operation.name][0]
        ) != id(operation):
            raise Exception(f"Input is duplicated: {operation.name}")
        else:
            INPUTS[party_name][operation.name] = (operation, ty)
        return {
            "InputReference": {
                "refers_to": operation.name,
            }
        }
    elif type(operation) == Map:
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        return {
            "Map": {
                "fn": operation.fn.id,
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Reduce:
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        return {
            "Reduce": {
                "fn": operation.fn.id,
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Zip:
        return {
            "Zip": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Unzip:
        return {
            "Unzip": {
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == NadaFunctionArg:
        return {
            "NadaFunctionArgRef": {
                "function_id": operation.function_id,
                "name": operation.name,
                "type": operation.type.__name__,
            }
        }

    else:
        raise Exception(f"Compilation of Operation {operation} not supported")

