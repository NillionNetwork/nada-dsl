"""
Compiler frontend consisting of wrapper functions for the classes and functions
that constitute the Nada embedded domain-specific language (EDSL).
"""

from dataclasses import dataclass, field
import os
from typing import List, Dict, Tuple
from sortedcontainers import SortedDict


from nada_mir_proto.nillion.nada.mir import v1 as proto_mir
from nada_mir_proto.nillion.nada.operations import v1 as proto_op
from nada_mir_proto.nillion.nada.types import v1 as proto_ty


from nada_dsl import Party
from nada_dsl.ast_util import (
    AST_OPERATIONS,
    ASTOperation,
    BinaryASTOperation,
    CastASTOperation,
    IfElseASTOperation,
    InputASTOperation,
    LiteralASTOperation,
    MapASTOperation,
    TupleAccessorASTOperation,
    NTupleAccessorASTOperation,
    NadaFunctionASTOperation,
    NadaFunctionArgASTOperation,
    NewASTOperation,
    ObjectAccessorASTOperation,
    RandomASTOperation,
    ReduceASTOperation,
    UnaryASTOperation,
)
from nada_dsl.timer import timer
from nada_dsl.source_ref import SourceRef
from nada_dsl.program_io import Output


@dataclass
class CompilationContext:
    """
    Compilation context that holds the state of the compilation process.
    """

    inputs: Dict[Tuple[str, str], InputASTOperation] = field(default_factory=SortedDict)
    parties: Dict[str, Party] = field(default_factory=SortedDict)
    functions: Dict[int, NadaFunctionASTOperation] = field(default_factory=lambda: {})
    literals: Dict[str, Tuple[str, proto_ty.NadaType]] = field(
        default_factory=lambda: {}
    )


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


def nada_compile(outputs: List[Output]) -> bytes:
    """Compile Nada to MIR and dump it as JSON."""
    compiled = nada_dsl_to_nada_mir(outputs)
    return bytes(compiled)


def nada_dsl_to_nada_mir(outputs: List[Output]) -> proto_mir.ProgramMir:
    """Convert Nada DSL to Nada MIR."""
    new_outputs = []
    ctx = CompilationContext()
    operations: Dict[int, proto_op.Operation] = SortedDict()
    # Process outputs
    for output in outputs:
        timer.start(
            f"nada_dsl.compiler_frontend.nada_dsl_to_nada_mir.{output.name}.process_operation"
        )
        out_operation_id = output.child.child.id
        traverse_and_process_operations(out_operation_id, operations, ctx)
        timer.stop(
            f"nada_dsl.compiler_frontend.nada_dsl_to_nada_mir.{output.name}.process_operation"
        )
        party = output.party
        ctx.parties[party.name] = party
        new_outputs.append(
            proto_mir.Output(
                operation_id=out_operation_id,
                name=output.name,
                party=party.name,
                type=AST_OPERATIONS[out_operation_id].ty,
                source_ref_index=output.source_ref.to_index(),
            )
        )

    operations = [
        proto_mir.OperationMapEntry(id=id, operation=op)
        for id, op in operations.items()
    ]

    mir = proto_mir.ProgramMir(
        functions=process_functions(ctx),
        parties=to_party_list(ctx.parties),
        inputs=to_input_list(ctx.inputs),
        literals=to_literal_list(ctx.literals),
        outputs=new_outputs,
        operations=operations,
        source_files=SourceRef.get_sources(),
        source_refs=SourceRef.get_refs(),
    )
    return mir


def to_party_list(parties: Dict[str, Party]) -> List[proto_mir.Party]:
    """Convert parties to a list in MIR format."""
    return [
        proto_mir.Party(
            name=party.name,
            source_ref_index=party.source_ref.to_index(),
        )
        for party in parties.values()
    ]


def to_input_list(inputs: Dict[int, InputASTOperation]) -> List[proto_mir.Input]:
    """Convert inputs to a list in MIR format."""
    input_list = []
    for input_ast in inputs.values():
        input_list.append(
            proto_mir.Input(
                name=input_ast.name,
                type=input_ast.ty,
                party=input_ast.party.name,
                doc=input_ast.doc,
                source_ref_index=input_ast.source_ref.to_index(),
            )
        )
    return input_list


def to_literal_list(
    literals: Dict[str, Tuple[str, proto_ty.NadaType]],
) -> List[proto_mir.Literal]:
    """Convert literals to a list in MIR format."""
    literal_list = []
    for name, (value, ty) in literals.items():
        literal_list.append(
            proto_mir.Literal(
                name=name,
                value=value,
                type=ty,
            )
        )
    return literal_list


def process_functions(
    ctx: CompilationContext,
) -> List[proto_mir.NadaFunction]:
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
    stack = list(ctx.functions.values())
    ctx.functions = {}
    while len(stack) > 0:
        function = stack.pop()
        function_operations = SortedDict()

        traverse_and_process_operations(
            function.child,
            function_operations,
            ctx,
        )
        if len(ctx.functions) > 0:
            stack.extend(ctx.functions.values())
            ctx.functions = {}

        function_operations = [
            proto_mir.OperationMapEntry(id=id, operation=op)
            for id, op in function_operations.items()
        ]

        mir_functions.append(function.to_mir(function_operations))
    return mir_functions


def add_input_to_map(
    operation: InputASTOperation, ctx: CompilationContext
) -> proto_op.Operation:
    """Adds an input to the global INPUTS dictionary"""
    ctx.parties[operation.party.name] = operation.party
    if (operation.party.name, operation.name) in ctx.inputs and ctx.inputs[
        (operation.party.name, operation.name)
    ].id != operation.id:
        raise CompilerException(f"Input is duplicated: {operation.name}")

    ctx.inputs[(operation.party.name, operation.name)] = operation
    return operation.to_mir()


class CompilerException(Exception):
    """Generic compiler exception"""


def traverse_and_process_operations(
    operation_id: int,
    operations: Dict[int, proto_op.Operation],
    ctx: CompilationContext,
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

    stack = [operation_id]
    while len(stack) > 0:
        operation_id = stack.pop()
        if operation_id not in operations:
            operation = AST_OPERATIONS[operation_id]
            maybe_op = process_operation(operation, ctx)
            if maybe_op is not None:
                operations[operation_id] = maybe_op
            stack.extend(operation.child_operations())


def process_operation(
    operation: ASTOperation, ctx: CompilationContext
) -> proto_op.Operation | None:
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
            TupleAccessorASTOperation,
            NTupleAccessorASTOperation,
            ObjectAccessorASTOperation,
        ),
    ):
        return operation.to_mir()

    if isinstance(operation, InputASTOperation):
        add_input_to_map(operation, ctx)
        return operation.to_mir()
    if isinstance(operation, LiteralASTOperation):
        ctx.literals[operation.literal_index] = (str(operation.value), operation.ty)
        return operation.to_mir()
    if isinstance(operation, (MapASTOperation, ReduceASTOperation)):
        if operation.fn not in ctx.functions:
            ctx.functions[operation.fn] = AST_OPERATIONS[operation.fn]
        return operation.to_mir()
    if isinstance(operation, NadaFunctionASTOperation):
        if operation.id not in ctx.functions:
            ctx.functions[operation.id] = AST_OPERATIONS[operation.id]
        return None

    raise CompilerException(f"Compilation of Operation {operation} is not supported")


class PrintMirException(Exception):
    """Generic exception for printing MIR"""


def print_mir(mir: proto_mir.ProgramMir):
    """Prints the MIR in a human-readable format."""
    print("Parties:")
    for party in mir.parties:
        print(f"  {party.name}")
    print("Inputs:")
    for mir_input in mir.inputs:
        print(
            f"  {mir_input.name} ty({type_to_str(mir_input.type)}) party({mir_input.party})"
        )
    print("Literals:")
    for literal in mir.literals:
        print(f"  {literal.name} ty({type_to_str(literal.type)}) val({literal.value})")
    print("Outputs:")
    for output in mir.outputs:
        print(
            f"  {output.name} ty({type_to_str(output.type)}) oid({output.operation_id})"
        )
    print("Functions:")
    for function in mir.functions:
        args = ", ".join(
            [f"{arg.name}: ty({type_to_str(arg.type)})" for arg in function.args]
        )
        print(f"  {function.name} fn_id({function.id}), args({args})")
        print_operations(function.operations)

    print("Operations:")
    print_operations(mir.operations)


# pylint: disable=too-many-branches
def print_operations(operation: List[proto_mir.OperationMapEntry]):
    """Prints a list of operations in a human-readable format."""
    print()
    for entry in operation:
        op_id, op = entry.id, entry.operation
        line = f"oid({op_id}) rty({type_to_str(op.type)}) = "
        if hasattr(op, "binary"):
            line += f"{op.binary.variant} oid({op.binary.left}) oid({op.binary.right})"
        elif hasattr(op, "unary"):
            line += f"{op.unary.variant} oid({op.unary.this})"
        elif hasattr(op, "cast"):
            line += f"cast oid({op.cast.target})"
        elif hasattr(op, "ifelse"):
            line += f"ifelse cond({op.ifelse.cond}) true({op.ifelse.first}) false({op.ifelse.second})"
        elif hasattr(op, "random"):
            line += "random "
        elif hasattr(op, "input_ref"):
            line += f"input_ref to({op.input_ref.refers_to})"
        elif hasattr(op, "arg_ref"):
            line += (
                f"arg_ref fn_id({op.arg_ref.function_id}) to({op.arg_ref.refers_to})"
            )
        elif hasattr(op, "literal_ref"):
            line += f"literal_ref to({op.literal_ref.refers_to})"
        elif hasattr(op, "map"):
            line += f"map fn({(op.map.fn)}) oid({op.map.child})"
        elif hasattr(op, "reduce"):
            line += f"reduce fn({(op.reduce.fn)}) init({op.reduce.initial}) oid({op.reduce.child})"
        elif hasattr(op, "new"):
            oids = ", ".join([f"oid({oid})" for oid in op.new.elements])
            line += f"new {oids}"
        elif hasattr(op, "array_accessor"):
            line += f"array_accessor oid({op.array_accessor.source}) {op.array_accessor.index}"
        elif hasattr(op, "tuple_accessor"):
            line += f"tuple_accessor oid({op.tuple_accessor.source}) {op.tuple_accessor.index}"
        elif hasattr(op, "ntuple_accessor"):
            line += f"ntuple_accessor oid({op.ntuple_accessor.source}) {op.ntuple_accessor.index}"
        elif hasattr(op, "object_accessor"):
            line += f"object_accessor oid({op.object_accessor.source}) {op.object_accessor.key}"
        elif hasattr(op, "cast"):
            line += f"cast oid({op.cast.target}) {op.cast.to}"
        else:
            raise PrintMirException(f"Unknown operation {op}")
        print(line)


# pylint: disable=too-many-branches,too-many-return-statements
def type_to_str(ty: proto_ty.NadaType):
    """Converts a Nada type to a string."""
    if hasattr(ty, "integer"):
        return "Integer"
    if hasattr(ty, "unsigned_integer"):
        return "UnsignedInteger"
    if hasattr(ty, "boolean"):
        return "Boolean"
    if hasattr(ty, "secret_integer"):
        return "SecretInteger"
    if hasattr(ty, "secret_unsigned_integer"):
        return "SecretUnsignedInteger"
    if hasattr(ty, "secret_boolean"):
        return "SecretBoolean"
    if hasattr(ty, "ecdsa_private_key"):
        return "EcdsaPrivateKey"
    if hasattr(ty, "ecdsa_digest_message"):
        return "EcdsaDigestMessage"
    if hasattr(ty, "ecdsa_signature"):
        return "EcdsaSignature"
    if hasattr(ty, "array"):
        return f"Array[{type_to_str(ty.collection.contained_type)}:{ty.collection.array.size}]"
    if hasattr(ty, "tuple"):
        return f"Tuple[{type_to_str(ty.tuple.left)}, {type_to_str(ty.tuple.right)}]"
    if hasattr(ty, "object"):
        return "Object"
    if hasattr(ty, "ntuple"):
        return f"NTuple[{', '.join([type_to_str(t) for t in ty.ntuple.fields])}]"
    raise PrintMirException("Unknown type {ty}")
