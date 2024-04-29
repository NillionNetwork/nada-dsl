"""
Compiler frontend consisting of wrapper functions for the classes and functions
that constitute the Nada embedded domain-specific language (EDSL).
"""
import hashlib
import json
import os
from json import JSONEncoder
import inspect
from typing import List, Dict, Any

from nada_dsl.source_ref import SourceRef
from nada_dsl.circuit_io import Input, Output, Party, Literal
from nada_dsl.nada_types.types import Integer, UnsignedInteger, Boolean
from nada_dsl.nada_types.collections import (
    Array,
    ArrayNew,
    TupleNew,
    Vector,
    Tuple,
    ArrayType,
    VectorType,
    TupleType,
)
from nada_dsl.nada_types.function import NadaFunction, NadaFunctionCall
from nada_dsl.future.operations import Cast
from nada_dsl.operations import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Modulo,
    Power,
    RightShift,
    LeftShift,
    LessThan,
    GreaterThan,
    LessOrEqualThan,
    GreaterOrEqualThan,
    PublicOutputEquality,
    Equals,
    Unzip,
    Random,
    IfElse,
    Reveal,
    TruncPr
)

from nada_dsl.nada_types.collections import (
    Map,
    Reduce,
    Zip,
)

INPUTS = {}
PARTIES = {}
FUNCTIONS = {}
LITERALS = {}


class ClassEncoder(JSONEncoder):
    """Custom JSON encoder for classes."""

    def default(self, o):
        if inspect.isclass(o):
            return o.__name__
        return {type(o).__name__: o.__dict__}


def get_target_dir() -> str:
    """Get the target directory for compilation output."""
    env_dir = os.environ.get("Nada_TARGET_DIR")
    if env_dir:
        return env_dir

    cwd = os.getcwd()

    try:
        os.mkdir("target")
    except FileExistsError:
        pass

    return os.path.join(cwd, "target")


def nada_compile(outputs: List[Output]) -> str:
    """Compile Nada to MIR and dump it as JSON."""
    compiled = nada_dsl_to_nada_mir(outputs)
    return json.dumps(compiled)


def nada_dsl_to_nada_mir(outputs: List[Output]) -> Dict[str, Any]:
    """Convert Nada DSL to Nada MIR."""
    new_outputs = []
    PARTIES.clear()
    INPUTS.clear()
    LITERALS.clear()
    instructions = {}
    for output in outputs:
        out_instruction_id = process_operation(output.inner, instructions)
        party = output.party
        PARTIES[party.name] = party
        new_outputs.append(
            {
                "instruction_id": out_instruction_id,
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
        "literals": to_literal_list(LITERALS),
        "outputs": new_outputs,
        "instructions": instructions,
        "source_files": SourceRef.get_sources(),
    }


def to_party_list(parties):
    """Convert parties to a list."""
    return [
        {
            "name": party.name,
            "source_ref": party.source_ref.to_dict(),
        }
        for party in parties.values()
    ]


def to_input_list(inputs):
    """Convert inputs to a list."""
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


def to_literal_list(literals):
    """Convert literals to a list."""
    literal_list = []
    for name, (value, ty) in literals.items():
        literal_list.append(
            {
                "name": name,
                "value": str(value),
                "type": ty,
            }
        )
    return literal_list


def to_function_list(functions: Dict[int, NadaFunction]) -> List[Dict]:
    """Convert functions to a list."""
    return [to_fn_dict(function) for function in functions.values()]


def to_type_dict(op_wrapper):
    """Convert operation wrapper to a dictionary representing its type."""
    if type(op_wrapper) == Array or type(op_wrapper) == ArrayType:
        size = {"size": op_wrapper.size} if op_wrapper.size else {}
        from typing import TypeVar

        inner_type = (
            "T"
            if type(op_wrapper.inner_type) == TypeVar
            else to_type_dict(op_wrapper.inner_type)
        )
        return {"Array": {"inner_type": inner_type, **size}}
    elif type(op_wrapper) == Vector or type(op_wrapper) == VectorType:
        from typing import TypeVar

        inner_type = (
            "T"
            if type(op_wrapper.inner_type) == TypeVar
            else to_type_dict(op_wrapper.inner_type)
        )
        return {"Vector": {"inner_type": inner_type}}
    elif type(op_wrapper) == Tuple or type(op_wrapper) == TupleType:
        return {
            "Tuple": {
                "left_type": to_type_dict(op_wrapper.left_type),
                "right_type": to_type_dict(op_wrapper.right_type),
            }
        }
    elif inspect.isclass(op_wrapper):
        return to_type(op_wrapper.__name__)
    else:
        return to_type(op_wrapper.__class__.__name__)


def to_type(name: str):
    """Convert a type name."""
    # Rename public variables so they are considered as the same as literals.
    if name.startswith("Public"):
        name = name[len("Public"):].lstrip()
        return name
    else:
        return name


def to_fn_dict(fn: NadaFunction):
    """Convert a function to a dictionary."""

    instructions = {}
    op_id = process_operation(fn.inner, instructions)
    return {
        "id": fn.id,
        "args": [
            {
                "name": arg.name,
                "type": to_type_dict(arg.type),
                "source_ref": arg.source_ref.to_dict(),
            }
            for arg in fn.args
        ],
        "function": fn.function.__name__,
        "return_instruction_id": op_id,
        "instructions": instructions,
        "return_type": to_type_dict(fn.return_type),
        "source_ref": fn.source_ref.to_dict(),
    }


def process_operation(operation_wrapper, instructions):
    """Process an operation."""
    from nada_dsl.nada_types.function import NadaFunctionArg

    ty = to_type_dict(operation_wrapper)
    operation = operation_wrapper.inner

    if isinstance(
            operation,
            (
                    Addition,
                    Subtraction,
                    Multiplication,
                    Division,
                    Modulo,
                    Power,
                    RightShift,
                    LeftShift,
                    LessThan,
                    GreaterThan,
                    GreaterOrEqualThan,
                    LessOrEqualThan,
                    Equals,
                    PublicOutputEquality,
                    Zip,
            ),
    ):
        op_id = id(operation)
        op_instruction = {
            type(operation).__name__: {
                "id": op_id,
                "left": process_operation(operation.left, instructions),
                "right": process_operation(operation.right, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id

    elif isinstance(operation, Cast):
        op_id = id(operation)
        op_instruction = {
            "Cast": {
                "id": op_id,
                "target": process_operation(operation.target, instructions),
                "to": operation.to.__name__,
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Input):
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
        op_id = id(operation)
        op_instruction = {
            "InputReference": {
                "id": op_id,
                "refers_to": operation.name,
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Literal):
        # Generate a unique name depending on the value and type to prevent duplicating literals in the bytecode.
        literal_name = hashlib.md5(
            (str(operation.value) + str(ty)).encode("UTF-8")
        ).hexdigest()
        LITERALS[literal_name] = (str(operation.value), ty)
        op_id = id(operation)
        op_instruction = {
            "LiteralReference": {
                "id": op_id,
                "refers_to": literal_name,
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Map):
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        op_id = id(operation)
        op_instruction = {
            "Map": {
                "id": op_id,
                "fn": operation.fn.id,
                "inner": process_operation(operation.inner, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Reduce):
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        op_id = id(operation)
        op_instruction = {
            "Reduce": {
                "id": op_id,
                "fn": operation.fn.id,
                "inner": process_operation(operation.inner, instructions),
                "initial": process_operation(operation.initial, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Unzip):
        op_id = id(operation)
        op_instruction = {
            "Unzip": {
                "id": op_id,
                "inner": process_operation(operation.inner, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, NadaFunctionArg):
        op_id = id(operation)
        op_instruction = {
            "NadaFunctionArgRef": {
                "id": op_id,
                "function_id": operation.function_id,
                "refers_to": operation.name,
                "type": to_type_dict(operation.type),
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, NadaFunctionCall):
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        op_id = id(operation)
        op_instruction = {
            "NadaFunctionCall": {
                "id": op_id,
                "function_id": operation.fn.id,
                "args": [process_operation(arg, instructions) for arg in operation.args],
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
                "return_type": to_type_dict(operation.fn.return_type),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Random):
        op_id = id(operation)
        op_instruction = {
            "Random": {
                "id": op_id,
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, IfElse):
        op_id = id(operation)
        op_instruction = {
            "IfElse": {
                "id": op_id,
                "this": process_operation(operation.this, instructions),
                "arg_0": process_operation(operation.arg_0, instructions),
                "arg_1": process_operation(operation.arg_1, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, Reveal):
        op_id = id(operation)
        op_instruction = {
            "Reveal": {
                "id": op_id,
                "this": process_operation(operation.this, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, TruncPr):
        op_id = id(operation)
        op_instruction = {
            "TruncPr": {
                "id": op_id,
                "left": process_operation(operation.left, instructions),
                "right": process_operation(operation.right, instructions),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, ArrayNew):
        op_id = id(operation)
        op_instruction = {
            "New": {
                "id": op_id,
                "elements": [process_operation(arg, instructions) for arg in operation.inner],
                "type": to_type_dict(operation.inner_type),
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    elif isinstance(operation, TupleNew):
        op_id = id(operation)
        op_instruction = {
            "New": {
                "id": op_id,
                "elements": [process_operation(operation.inner[0], instructions),
                             process_operation(operation.inner[1], instructions)],
                "type": to_type_dict(operation.inner_type),
                "source_ref": operation.source_ref.to_dict(),
            }
        }
        instructions[op_id] = op_instruction
        return op_id
    else:
        raise Exception(f"Compilation of Operation {operation} is not supported")
