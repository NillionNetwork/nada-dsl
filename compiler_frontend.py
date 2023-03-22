import json
import os
from json import JSONEncoder
import inspect
from typing import List, Optional, Dict, Any

from nada_dsl.source_ref import SourceRef
from nada_dsl.circuit_io import Input, Output
from nada_dsl.nada_types.rational import SecretFixedPointRational
from nada_dsl.future.nada_types.collections import (
    Array,
    Vector,
    NadaTuple,
    ArrayType,
    VectorType,
    NadaTupleType,
)
from nada_dsl.future.nada_types.function import NadaFunction
from nada_dsl.future.operations import Cast, Map, Reduce, Zip, Unzip
from nada_dsl.operations import Addition, Multiplication, CompareLessThan


class ClassEncoder(JSONEncoder):
    def default(self, o):
        if inspect.isclass(o):
            return o.__name__
        return {type(o).__name__: o.__dict__}


class CompilationPlaceholder:
    outputs: Optional[List[Output]] = None

    def initialize(self, outputs: List[Output]) -> None:
        if self.outputs is not None:
            raise Exception("only one `nada_compile` call is allowed per program")
        self.outputs = outputs

    def retrieve(self) -> str:
        if self.outputs is None:
            raise Exception("no `nada_compile` calls found")
        compiled = nada_dsl_to_nada_mir(self.outputs)
        return json.dumps(compiled)


COMPILATION_PLACEHOLDER = CompilationPlaceholder()


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


def nada_compile(outputs: List[Output]):
    COMPILATION_PLACEHOLDER.initialize(outputs)


def nada_retrieve() -> str:
    return COMPILATION_PLACEHOLDER.retrieve()


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
    for output in outputs:
        new_out = process_operation(output.inner)
        new_outputs.append(
            {
                "inner": new_out,
                "name": output.name,
                "party": {
                    "name": output.party.name,
                    "source_ref": output.party.source_ref.to_dict(),
                },
                "type": to_type_dict(output.inner),
                "source_ref": output.source_ref.to_dict(),
            }
        )

    return {
        "outputs": new_outputs,
        "source_files": SourceRef.get_sources(),
    }


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
        "args": [{"name": arg.name, "type": arg.type.__name__} for arg in fn.args],
        "function": fn.function.__name__,
        "inner": process_operation(fn.inner),
        "return_type": fn.return_type.__name__,
    }


def process_operation(operation_wrapper):
    from nada_dsl.future.nada_types.function import NadaFunctionArg

    ty = to_type_dict(operation_wrapper)
    operation = operation_wrapper.inner

    if type(operation) == Addition:
        return {
            "Addition": {
                "right": process_operation(operation.right),
                "left": process_operation(operation.left),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Multiplication:
        return {
            "Multiplication": {
                "right": process_operation(operation.right),
                "left": process_operation(operation.left),
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
        return {
            "Input": {
                "type": ty,
                "party": {
                    "name": operation.party.name,
                    "source_ref": operation.party.source_ref.to_dict(),
                },
                "name": operation.name,
                "doc": operation.doc,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Map:
        return {
            "Map": {
                "fn": to_fn_dict(operation.fn),
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == Reduce:
        return {
            "Reduce": {
                "fn": to_fn_dict(operation.fn),
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
    elif type(operation) == CompareLessThan:
        return {
            "CompareLessThan": {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif type(operation) == NadaFunctionArg:
        return {
            "NadaFunctionArg": {
                "name": operation.name,
                "type": operation.type.__name__,
            }
        }

    else:
        raise Exception(f"Compilation of Operation {operation} not supported")
