import inspect
from dataclasses import dataclass
from typing import Generic, List, Callable

from nada_dsl import SourceRef
from nada_dsl.nada_types.generics import T, R
from nada_dsl.nada_types import NadaType


@dataclass
class NadaFunctionArg(Generic[T]):
    function_id: int
    name: str
    type: T
    source_ref: SourceRef


@dataclass
class NadaFunction(NadaType, Generic[T, R]):
    id: int
    args: List[NadaFunctionArg]
    function: Callable[[T], R]
    return_type: R
    source_ref: SourceRef

    def __call__(self, *args, **kwargs) -> R:
        return self.return_type(inner=NadaFunctionCall(self, args, source_ref=SourceRef.back_frame())) # type: ignore

class NadaFunctionCall(NadaType, Generic[R]):
    """Represents a call to a Nada Function."""
    fn: NadaFunction
    args: List[NadaType]
    source_ref: SourceRef

    def __init__(self, nada_function, args, source_ref):
        self.args = args
        self.fn = nada_function
        self.source_ref = source_ref

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
    for idx, arg in enumerate(args.args):
        arg_type = args_ty[arg] if args_ty else args.annotations[arg]
        arg_type = inner_type(arg_type)
        # We'll get the function source ref for now
        nada_arg = NadaFunctionArg(
            function_id=id(fn),
            name=arg,
            type=arg_type,
            source_ref=SourceRef.back_frame(),
        )
        nada_args.append(nada_arg)

    nada_args_type_wrapped = []
    from copy import copy

    for arg in nada_args:
        arg_type = copy(arg.type)
        arg_type.inner = arg
        nada_args_type_wrapped.append(arg_type)

    inner = fn(*nada_args_type_wrapped)
    return_type = return_ty if return_ty else args.annotations["return"]
    return NadaFunction(
        id=id(fn),
        function=fn,
        args=nada_args,
        inner=inner,
        return_type=return_type,
        source_ref=SourceRef.back_frame(),
    )
