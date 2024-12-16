"""function.py

Nada function definitions and utilities.
"""

import inspect
from typing import Generic, List, Callable

from nada_mir_proto.nillion.nada.types import v1 as proto_ty

from nada_dsl import SourceRef
from nada_dsl.ast_util import (
    AST_OPERATIONS,
    NadaFunctionASTOperation,
    NadaFunctionArgASTOperation,
    OperationId,
)
from nada_dsl.nada_types.generics import T, R
from nada_dsl.nada_types import DslType


class NadaFunctionArg(Generic[T]):
    """Represents a Nada function argument."""

    function_id: int
    name: str
    type: T
    source_ref: SourceRef

    def __init__(self, function_id: int, name: str, arg_type: T, source_ref: SourceRef):
        self.id = OperationId.next()
        self.function_id = function_id
        self.name = name
        self.type = arg_type
        self.source_ref = source_ref
        self.store_in_ast(arg_type.to_mir())

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store object in AST."""
        AST_OPERATIONS[self.id] = NadaFunctionArgASTOperation(
            id=self.id,
            name=self.name,
            fn=self.function_id,
            ty=ty,
            source_ref=self.source_ref,
        )


class NadaFunction(Generic[T, R]):
    """Nada Function.

    Represents a Nada Function. Nada functions are special types of functions that are used
    in map / reduce operations.
    """

    id: int
    args: List[NadaFunctionArg]
    function: Callable[[T], R]
    return_type: R
    source_ref: SourceRef

    def __init__(
        self,
        function_id: int,
        args: List[NadaFunctionArg],
        function: Callable[[T], R],
        return_type: R,
        source_ref: SourceRef,
        child: DslType,
    ):
        self.child = child
        self.id = function_id
        self.args = args
        self.function = function

        self.return_type = return_type
        self.source_ref = source_ref
        self.store_in_ast()

    def store_in_ast(self):
        """Store this Nada Function in AST."""
        AST_OPERATIONS[self.id] = NadaFunctionASTOperation(
            name=self.function.__name__,
            args=[arg.id for arg in self.args],
            id=self.id,
            ty=self.return_type.to_mir(),
            source_ref=self.source_ref,
            child=self.child.child.id,
        )


def create_nada_fn(fn, args_ty) -> NadaFunction[T, R]:
    """
    Can be used also for lambdas
    ```python
    array.map(
        nada_fn(
            lambda x: x.cast(SecretInteger),
            args_ty={'x': SecretInteger}, return_ty=SecretInteger))
    ```
    """

    args = inspect.getfullargspec(fn)
    nada_args = []
    function_id = OperationId.next()
    nada_args_type_wrapped = []
    for arg, arg_ty in zip(args.args, args_ty):
        # We'll get the function source ref for now
        nada_arg = NadaFunctionArg(
            function_id,
            name=arg,
            arg_type=arg_ty,
            source_ref=SourceRef.back_frame(),
        )
        nada_args.append(nada_arg)
        nada_args_type_wrapped.append(arg_ty.instantiate(nada_arg))

    child = fn(*nada_args_type_wrapped)

    return_type = child.type()
    return NadaFunction(
        function_id,
        function=fn,
        args=nada_args,
        child=child,
        return_type=return_type,
        source_ref=SourceRef.back_frame(),
    )
