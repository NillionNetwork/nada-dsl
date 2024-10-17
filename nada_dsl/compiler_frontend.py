"""
Compiler frontend consisting of wrapper functions for the classes and functions
that constitute the Nada embedded domain-specific language (EDSL).
"""

from dataclasses import dataclass
import json
import os
from json import JSONEncoder
import inspect
from typing import List, Dict, Any, Optional, Tuple
from sortedcontainers import SortedDict

from nada_dsl.ast_util import (
    AST_OPERATIONS,
    ASTOperation,
    BinaryASTOperation,
    CastASTOperation,
    IfElseASTOperation,
    InputASTOperation,
    LiteralASTOperation,
    MapASTOperation,
    NadaFunctionASTOperation,
    NadaFunctionArgASTOperation,
    NadaFunctionCallASTOperation,
    NewASTOperation,
    RandomASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
)
from nada_dsl.timer import timer
from nada_dsl.source_ref import SourceRef
from nada_dsl.program_io import Output

INPUTS = SortedDict()
PARTIES = SortedDict()
FUNCTIONS: Dict[int, NadaFunctionASTOperation] = {}
LITERALS: Dict[str, Tuple[str, object]] = {}


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
    operations: Dict[int, Dict] = {}
    # Process outputs
    for output in outputs:
        timer.start(
            f"nada_dsl.compiler_frontend.nada_dsl_to_nada_mir.{output.name}.process_operation"
        )
        out_operation_id = output.inner.inner.id
        extra_fns = traverse_and_process_operations(
            out_operation_id, operations, FUNCTIONS
        )
        FUNCTIONS.update(extra_fns)

        timer.stop(
            f"nada_dsl.compiler_frontend.nada_dsl_to_nada_mir.{output.name}.process_operation"
        )
        party = output.party
        PARTIES[party.name] = party
        new_outputs.append(
            {
                "operation_id": out_operation_id,
                "name": output.name,
                "party": party.name,
                "type": AST_OPERATIONS[out_operation_id].ty,
                "source_ref_index": output.source_ref.to_index(),
            }
        )
    # Now we go through all the discovered functions and see if they are
    # invoking other functions, which we will need to process and add to the FUNCTIONS dictionary

    return {
        "functions": to_mir_function_list(FUNCTIONS),
        "parties": to_party_list(PARTIES),
        "inputs": to_input_list(INPUTS),
        "literals": to_literal_list(LITERALS),
        "outputs": new_outputs,
        "operations": operations,
        "source_files": SourceRef.get_sources(),
        "source_refs": SourceRef.get_refs(),
    }


def to_party_list(parties) -> List[Dict]:
    """Convert parties to a list in MIR format."""
    return [
        {
            "name": party.name,
            "source_ref_index": party.source_ref.to_index(),
        }
        for party in parties.values()
    ]


def to_input_list(inputs) -> List[Dict]:
    """Convert inputs to a list in MIR format."""
    input_list = []
    for party_inputs in inputs.values():
        for program_input, program_type in party_inputs.values():
            input_list.append(
                {
                    "name": program_input.name,
                    "type": program_type,
                    "party": program_input.party.name,
                    "doc": program_input.doc,
                    "source_ref_index": program_input.source_ref.to_index(),
                }
            )
    return input_list


def to_literal_list(literals: Dict[str, Tuple[str, object]]) -> List[Dict]:
    """Convert literals to a list in MIR format."""
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


def to_mir_function_list(functions: Dict[int, NadaFunctionASTOperation]) -> List[Dict]:
    """Convert functions to a list in MIR format.

    From a starting dictionary of functions, it traverses each one of them,
    generating the corresponding MIR representation, discovering all the operations
    in the function.

    The algorithm might find new function calls while processing the operations
    in a function. These function calls might discover of new functions that are not
    in the original dictionary. These functions will be processed in turn.

    This function is designed to be invoked after the initial operation discovery
    which will find the starting set of functions.

    Arguments
    ---------
    functions: Dict[int, NadaFunctionASTOperation]
        A dictionary containing a starting list of functions
    """
    mir_functions = []
    stack = list(functions.values())
    while len(stack) > 0:
        function = stack.pop()
        function_operations = {}

        extra_functions = traverse_and_process_operations(
            function.inner,
            function_operations,
            functions,
        )
        if extra_functions:
            stack.extend(extra_functions.values())
            functions.update(extra_functions)
        mir_functions.append(function.to_mir(function_operations))
    return mir_functions


def add_input_to_map(operation: InputASTOperation):
    """Adds an input to the global INPUTS dictionary"""
    party_name = operation.party.name
    PARTIES[party_name] = operation.party
    if party_name not in INPUTS:
        INPUTS[party_name] = {}
    if (
        operation.name in INPUTS[party_name]
        and INPUTS[party_name][operation.name][0].id != operation.id
    ):
        raise CompilerException(f"Input is duplicated: {operation.name}")

    INPUTS[party_name][operation.name] = (operation, operation.ty)
    return operation.to_mir()


class CompilerException(Exception):
    """Generic compiler exception"""


def traverse_and_process_operations(
    operation_id: int,
    operations: Dict[int, Dict],
    functions: Dict[int, NadaFunctionASTOperation],
) -> Dict[int, NadaFunctionASTOperation]:
    """Traverses the AST operations finding all the operation tree rooted at the given
    operation. Uses an iterative DFS algorithm.

    It invokes `process_operation` which in turn generates a MIR and optionally discover
    extra functions.

    Arguments
    ---------
    operation_id: int
        The identifier of the root operation where the algorithm will start traversing the
        operation graph
    operations: Dict[int, Dict]
        Dictionary that will be updated with the operations found
    functions: Dict[int, NadaFunctionASTOperation]
        Dictionary of existing functions. If a function is found that is not in this dictionary
        it will added to the result dictionary

    Returns
    -------
    Dict[int, NadaFunctionASTOperation]
        Dictionary with all the new functions being found while traversing the operation tree
    """

    extra_functions = {}
    stack = [operation_id]
    while len(stack) > 0:
        operation_id = stack.pop()
        if operation_id not in operations:
            operation = AST_OPERATIONS[operation_id]
            wrapped_operation = process_operation(operation, functions)
            operations[operation_id] = wrapped_operation.mir
            if wrapped_operation.extra_function:
                extra_functions[wrapped_operation.extra_function.id] = (
                    wrapped_operation.extra_function
                )
            stack.extend(operation.inner_operations())
    return extra_functions


@dataclass
class ProcessOperationOutput:
    """Output of the process_operation function"""

    mir: Dict[str, Dict]
    extra_function: Optional[NadaFunctionASTOperation]


def process_operation(
    operation: ASTOperation, functions: Dict[int, NadaFunctionASTOperation]
) -> ProcessOperationOutput:
    """Process an AST operation.

    For arithmetic operations it simply returns the MIR representation of the operation.

    For inputs and literal types, it adds the corresponding value to the appropriate
    dictionaries and returns the MIR representation.

    For map, reduce and function call operations, adds the nada function if it's not in the
    functions dictionary, and returns the MIR representation.

    Whenever it finds a nada function, it adds it if it's not there. But it does not generate
    a MIR representation as functions are processed separately.

    It ignores nada function arguments as they should not be present in the MIR.
    """
    processed_operation = None
    if isinstance(
        operation,
        (
            BinaryASTOperation,
            UnaryASTOperation,
            CastASTOperation,
            IfElseASTOperation,
            NewASTOperation,
            RandomASTOperation,
            NadaFunctionArgASTOperation,
        ),
    ):
        processed_operation = ProcessOperationOutput(operation.to_mir(), None)

    elif isinstance(operation, InputASTOperation):
        add_input_to_map(operation)
        processed_operation = ProcessOperationOutput(operation.to_mir(), None)
    elif isinstance(operation, LiteralASTOperation):

        LITERALS[operation.literal_index] = (str(operation.value), operation.ty)
        processed_operation = ProcessOperationOutput(operation.to_mir(), None)
    elif isinstance(
        operation, (MapASTOperation, ReduceASTOperation, NadaFunctionCallASTOperation)
    ):
        extra_fn = None
        if operation.fn not in functions:
            extra_fn = AST_OPERATIONS[operation.fn]

        processed_operation = ProcessOperationOutput(operation.to_mir(), extra_fn)  # type: ignore
    elif isinstance(operation, NadaFunctionASTOperation):
        extra_fn = None
        if operation.id not in functions:
            extra_fn = AST_OPERATIONS[operation.id]
        processed_operation = ProcessOperationOutput({}, extra_fn)  # type: ignore
    else:
        raise CompilerException(
            f"Compilation of Operation {operation} is not supported"
        )
    return processed_operation
