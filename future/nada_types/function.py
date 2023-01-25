import inspect
from dataclasses import dataclass
from typing import Generic, List, Callable

from nada_dsl import SourceRef
from nada_dsl.future.nada_types.generics import T, R
from nada_dsl.nada_types import NadaType


@dataclass
class NadaFunctionArg(Generic[T]):
    name: str
    type: T


@dataclass
class NadaFunction(NadaType, Generic[T, R]):
    args: List[NadaFunctionArg]
    function: Callable[[T], R]
    return_type: R
    source_ref: SourceRef

    def __call__(self, *args, **kwargs) -> R:
        return self.function(*args, **kwargs)


def nada_fn(fn, args_ty=None, return_ty=None) -> NadaFunction[T, R]:
    """
    Can be use also for lambdas
    ```python
    array.map(nada_fn(lambda x: x.cast(SecretBigInteger), args_ty={'x': SecretInteger8}, return_ty=SecretBigInteger))
    ```
    """

    args = inspect.getfullargspec(fn)
    nada_args = []
    for idx, arg in enumerate(args.args):
        arg_type = args_ty[arg] if args_ty else args.annotations[arg]
        nada_arg = NadaFunctionArg(name=arg, type=arg_type)
        nada_args.append(nada_arg)

    nada_args_type_wrapped = []
    for arg in nada_args:
        nada_args_type_wrapped.append(arg.type(inner=arg))

    inner = fn(*nada_args_type_wrapped)
    return_type = return_ty if return_ty else args.annotations['return']
    return NadaFunction(
        function=fn,
        args=nada_args,
        inner=inner,
        return_type=return_type,
        source_ref=SourceRef.back_frame()
    )
