"""function.py

Nada function definitions and utilities.
"""

import inspect
from dataclasses import dataclass
from typing import Generic, List, Callable
from copy import copy
from nada_dsl import SourceRef
from nada_dsl.ast_util import (
    AST_OPERATIONS,
    NadaFunctionASTOperation,
    NadaFunctionArgASTOperation,
    NadaFunctionCallASTOperation,
    next_operation_id,
)
from nada_dsl.nada_types.generics import T, R
from nada_dsl.nada_types import Mode, NadaType
from nada_dsl.nada_types.scalar_types import ScalarType
from nada_dsl.errors import NotAllowedException


class NadaFunctionArg(Generic[T]):
    """Represents a Nada function argument."""

    function_id: int
    name: str
    type: T
    source_ref: SourceRef

    def __init__(self, function_id: int, name: str, arg_type: T, source_ref: SourceRef):
        self.id = next_operation_id()
        self.function_id = function_id
        self.name = name
        self.type = arg_type
        self.source_ref = source_ref
        self.store_in_ast(arg_type.to_type())

    def store_in_ast(self, ty):
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

    They are decorated using the `@nada_fn` decorator.
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
        inner: NadaType,
    ):
        if issubclass(return_type, ScalarType) and return_type.mode == Mode.CONSTANT:
            raise NotAllowedException(
                "Nada functions with literal return types are not allowed"
            )
        # Nada functions with literal argument types are not supported.
        # This is because the compiler consolidates operations between literals.
        if all(
            issubclass(arg.type.__class__, ScalarType)
            and arg.type.mode == Mode.CONSTANT
            for arg in args
        ):
            raise NotAllowedException(
                "Nada functions with literal argument types are not allowed"
            )
        self.inner = inner
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
            ty=self.return_type.class_to_type(),
            source_ref=self.source_ref,
            inner=self.inner.inner.id,
        )

    def __call__(self, *args, **kwargs) -> R:
        return self.return_type(
            inner=NadaFunctionCall(self, args, source_ref=SourceRef.back_frame())
        )


@dataclass
class NadaFunctionCall(Generic[R]):
    """Represents a call to a Nada Function."""

    fn: NadaFunction
    args: List[NadaType]
    source_ref: SourceRef

    def __init__(self, nada_function, args, source_ref):
        self.id = next_operation_id()
        self.args = args
        self.fn = nada_function
        self.source_ref = source_ref
        self.store_in_ast(nada_function.return_type.class_to_type())

    def store_in_ast(self, ty):
        """Store this function call in the AST."""
        AST_OPERATIONS[self.id] = NadaFunctionCallASTOperation(
            id=self.id,
            args=[arg.inner.id for arg in self.args],
            fn=self.fn.id,
            source_ref=self.source_ref,
            ty=ty,
        )


def inner_type(ty):
    """Utility function that calculates the inner type for a function argument."""

    origin_ty = getattr(ty, "__origin__", ty)
    if not issubclass(origin_ty, ScalarType):
        inner_ty = getattr(ty, "__args__", None)
        inner_ty = inner_type(inner_ty[0]) if inner_ty else T
        return origin_ty.init_as_template_type(inner_ty)
    if origin_ty.mode == Mode.CONSTANT:
        return origin_ty(value=0)
    return origin_ty(inner=None)


def nada_fn(fn, args_ty=None, return_ty=None) -> NadaFunction[T, R]:
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
    function_id = next_operation_id()
    for arg in args.args:
        arg_type = args_ty[arg] if args_ty else args.annotations[arg]
        arg_type = inner_type(arg_type)
        # We'll get the function source ref for now
        nada_arg = NadaFunctionArg(
            function_id,
            name=arg,
            arg_type=arg_type,
            source_ref=SourceRef.back_frame(),
        )
        nada_args.append(nada_arg)

    nada_args_type_wrapped = []

    for arg in nada_args:
        arg_type = copy(arg.type)
        arg_type.inner = arg
        nada_args_type_wrapped.append(arg_type)

    inner = fn(*nada_args_type_wrapped)

    return_type = return_ty if return_ty else args.annotations["return"]
    return NadaFunction(
        function_id,
        function=fn,
        args=nada_args,
        inner=inner,
        return_type=return_type,
        source_ref=SourceRef.back_frame(),
    )
