import json
import os

from circuit_io import Input, Output
from future.operations import Cast
from operations import Addition, Multiplication


def compile(outputs: [Output], output_file: str):
    outputs = typed_circuit_to_untyped(outputs)

    json_circuit = json.dumps(outputs, indent=2)

    print(json_circuit)

    try:
        os.mkdir("target")
    except FileExistsError:
        pass

    with open(f"./target/{output_file}.circuit.json", "w") as file:
        file.write(json_circuit)

    cwd = os.getcwd()

    os.system(f'sh -c "cd ../compiler-backend && cargo run -- {cwd}/target/{output_file}.circuit.json {output_file}"')


def typed_circuit_to_untyped(outputs: [Output]) -> [dict]:
    new_outputs = []
    for output in outputs:
        new_out = process_operation(output.inner)
        new_outputs.append({
            "inner": new_out,
            "name": output.name,
            "type": type(output.inner).__name__,
            "lineno": output.lineno,
            "file": output.file
        })
    return new_outputs


def process_operation(operation):
    type_name = operation.__class__.__name__
    operation = operation.inner
    if type(operation) == Addition:
        return {
            'Addition': {
                'right': process_operation(operation.right),
                'left': process_operation(operation.left),
                'lineno': operation.lineno,
                'file': operation.file,
                'type': type_name
            }
        }
    elif type(operation) == Multiplication:
        return {
            'Multiplication': {
                'right': process_operation(operation.right),
                'left': process_operation(operation.left),
                'lineno': operation.lineno,
                'file': operation.file,
                'type': type_name
            }
        }
    elif type(operation) == Cast:
        return {
            'Cast': {
                'target': process_operation(operation.target),
                'to': operation.to.__name__,
                'lineno': operation.lineno,
                'file': operation.file,
                'type': type_name
            }
        }
    elif type(operation) == Input:
        return {
            'Input': {
                'type': type_name,
                'party': {
                    "name": operation.party.name,
                    'lineno': operation.party.lineno,
                    'file': operation.party.file,
                },
                'name': operation.name,
                'lineno': operation.lineno,
                'file': operation.file,
            }
        }
    else:
        raise Exception(f"Compilation of Operation {operation} not supported")
