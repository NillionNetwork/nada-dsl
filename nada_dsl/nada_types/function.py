"""function.py

Nada functions and utilities.
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
)
from nada_dsl.nada_types.generics import T, R
from nada_dsl.nada_types import NadaType


class NadaFunctionArg(Generic[T]):
    function_id: int
    name: str
    type: T
    source_ref: SourceRef

    def __init__(self, function_id: int, name: str, arg_type: T, source_ref: SourceRef):
        self.id = id(self)
        self.function_id = function_id
        self.name = name
        self.type = arg_type
        self.source_ref = source_ref
        self.store_in_ast(arg_type.to_type())

    def store_in_ast(self, ty):
        AST_OPERATIONS[self.id] = NadaFunctionArgASTOperation(
            id=self.id,
            name=self.name,
            fn=self.function_id,
            ty=ty,
            source_ref=self.source_ref,
        )


class NadaFunction(Generic[T, R]):
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
        self.inner = inner
        self.id = function_id
        self.args = args
        self.function = function
        self.return_type = return_type
        self.source_ref = source_ref
        self.store_in_ast()

    def store_in_ast(self):
        AST_OPERATIONS[self.id] = NadaFunctionASTOperation(
            name=self.function.__name__,
            args=[arg.id for arg in self.args],
            id=self.id,
            ty=self.return_type.class_to_type(),
            source_ref=self.source_ref,
            inner=self.inner.inner.id,
        )

    def __call__(self, *args, **kwargs) -> R:
        return self.return_type(inner=NadaFunctionCall(self, args, source_ref=SourceRef.back_frame()))  # type: ignore


@dataclass
class NadaFunctionCall(Generic[R]):
    """Represents a call to a Nada Function."""

    fn: NadaFunction
    args: List[NadaType]
    source_ref: SourceRef

    def __init__(self, nada_function, args, source_ref):
        self.id = id(self)
        self.args = args
        self.fn = nada_function
        self.source_ref = source_ref
        self.store_in_ast(nada_function.return_type.class_to_type())

    def store_in_ast(self, ty):
        AST_OPERATIONS[self.id] = NadaFunctionCallASTOperation(
            id=self.id,
            args=[arg.inner.id for arg in self.args],
            fn=self.fn.id,
            source_ref=self.source_ref,
            ty=ty,
        )


def inner_type(ty):
    from nada_dsl import Vector, Array

    origin_ty = getattr(ty, "__origin__", ty)
    if origin_ty == Array or origin_ty == Vector:
        inner_ty = getattr(ty, "__args__", None)
        inner_ty = inner_type(inner_ty[0]) if inner_ty else T
        return origin_ty.init_as_template_type(inner_ty)
    else:
        return origin_ty(inner=None)


def nada_fn(fn, args_ty=None, return_ty=None) -> NadaFunction[T, R]:
    """
    Can be used also for lambdas
    ```python
    array.map(nada_fn(lambda x: x.cast(SecretInteger), args_ty={'x': SecretInteger}, return_ty=SecretInteger))
    ```
    """

    args = inspect.getfullargspec(fn)
    nada_args = []
    for arg in args.args:
        arg_type = args_ty[arg] if args_ty else args.annotations[arg]
        arg_type = inner_type(arg_type)
        # We'll get the function source ref for now
        nada_arg = NadaFunctionArg(
            function_id=id(fn),
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
        function_id=id(fn),
        function=fn,
        args=nada_args,
        inner=inner,
        return_type=return_type,
        source_ref=SourceRef.back_frame(),
    )
