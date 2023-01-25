import json
import os
from json import JSONEncoder
import inspect

from circuit_io import Input, Output
from future.nada_types.collections import Array, Vector, NadaTuple, ArrayType, VectorType, NadaTupleType
from future.nada_types.function import NadaFunction
from future.operations import Cast, Map, Reduce, Zip, Unzip
from operations import Addition, Multiplication


class ClassEncoder(JSONEncoder):
    def default(self, o):
        if inspect.isclass(o):
            return o.__name__
        return {type(o).__name__: o.__dict__}


def compile(outputs: [Output], output_file: str):
    try:
        os.mkdir("target")
    except FileExistsError:
        pass

    nada_pydsl_hir = json.dumps(outputs, cls=ClassEncoder, indent=2)
    with open(f"./target/{output_file}.nada-pydsl-hir.json", "w") as file:
        file.write(nada_pydsl_hir)

    outputs = typed_circuit_to_untyped(outputs)

    nada_mir = json.dumps(outputs, indent=2)

    with open(f"./target/{output_file}.nada-mir.json", "w") as file:
        file.write(nada_mir)

    cwd = os.getcwd()

    os.system(
        f'sh -c "cd ../compiler-backend && RUST_BACKTRACE=1 cargo run -- {cwd}/target/{output_file}.nada-mir.json {output_file}"')


def typed_circuit_to_untyped(outputs: [Output]) -> [dict]:
    new_outputs = []
    for output in outputs:
        new_out = process_operation(output.inner)
        new_outputs.append({
            "inner": new_out,
            "name": output.name,
            "type": to_type_dict(output.inner),
            "lineno": output.lineno,
            "file": output.file
        })
    return new_outputs


def to_type_dict(op_wrapper):
    if type(op_wrapper) == Array or type(op_wrapper) == ArrayType:
        return {
            "Array": {
                "size": op_wrapper.size,
                "inner_type": to_type_dict(op_wrapper.inner_type)
            }
        }
    elif type(op_wrapper) == Vector or type(op_wrapper) == VectorType:
        return {
            "Vector": {
                "inner_type": to_type_dict(op_wrapper.inner_type)
            }
        }
    elif type(op_wrapper) == NadaTuple or type(op_wrapper) == NadaTupleType:
        return {
            "NadaTuple": {
                "left_type": to_type_dict(op_wrapper.left_type),
                "right_type": to_type_dict(op_wrapper.right_type),
            }
        }
    elif inspect.isclass(op_wrapper):
        return op_wrapper.__name__
    else:
        return op_wrapper.__class__.__name__


def get_inner(op_wrapper):
    return op_wrapper.inner


def to_fn_dict(fn: NadaFunction):
    return {
        'args': [{
            'name': arg.name,
            'type': arg.type.__name__
        } for arg in fn.args],
        'function': fn.function.__name__,
        'inner': process_operation(fn.inner),
        'return_type': fn.return_type.__name__,
    }


def process_operation(operation_wrapper):
    from future.nada_types.function import NadaFunctionArg

    ty = to_type_dict(operation_wrapper)
    operation = get_inner(operation_wrapper)

    if type(operation) == Addition:
        return {
            'Addition': {
                'right': process_operation(operation.right),
                'left': process_operation(operation.left),
                'lineno': operation.lineno,
                'file': operation.file,
                'type': ty
            }
        }
    elif type(operation) == Multiplication:
        return {
            'Multiplication': {
                'right': process_operation(operation.right),
                'left': process_operation(operation.left),
                'lineno': operation.lineno,
                'file': operation.file,
                'type': ty
            }
        }
    elif type(operation) == Cast:
        return {
            'Cast': {
                'target': process_operation(operation.target),
                'to': operation.to.__name__,
                'lineno': operation.lineno,
                'file': operation.file,
                'type': ty
            }
        }
    elif type(operation) == Input:
        return {
            'Input': {
                'type': ty,
                'party': {
                    "name": operation.party.name,
                    'lineno': operation.party.lineno,
                    'file': operation.party.file,
                },
                'name': operation.name,
                'doc': operation.doc,
                'lineno': operation.lineno,
                'file': operation.file,
            }
        }
    elif type(operation) == Map:
        return {
            'Map': {
                'fn': to_fn_dict(operation.fn),
                'inner': process_operation(operation.inner),
                'type': ty,
                'lineno': operation.lineno,
                'file': operation.file,
            }
        }
    elif type(operation) == Reduce:
        return {
            'Reduce': {
                'fn': to_fn_dict(operation.fn),
                'inner': process_operation(operation.inner),
                'type': ty,
                'lineno': operation.lineno,
                'file': operation.file,
            }
        }
    elif type(operation) == Zip:
        return {
            'Zip': {
                'left': process_operation(operation.left),
                'right': process_operation(operation.right),
                'type': ty,
                'lineno': operation.lineno,
                'file': operation.file,
            }
        }
    elif type(operation) == Unzip:
        return {
            'Unzip': {
                'inner': process_operation(operation.inner),
                'type': ty,
                'lineno': operation.lineno,
                'file': operation.file,
            }
        }
    elif type(operation) == NadaFunctionArg:
        return {
            'NadaFunctionArg': {
                'name': operation.name,
                'type': operation.type.__name__,
            }
        }

    else:
        raise Exception(f"Compilation of Operation {operation} not supported")
