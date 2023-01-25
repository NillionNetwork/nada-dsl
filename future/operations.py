from dataclasses import dataclass

from future.nada_types.function import NadaFunction
from future.nada_types.generics import T, R
from nada_types import AllTypes, AllTypesType, TypeInner
from util import get_back_file_lineno


@dataclass
class Cast:
    target: AllTypes
    to: AllTypesType
    lineno: str
    file: str


@dataclass
class Map:
    inner: TypeInner
    fn: NadaFunction[T, R]
    lineno: str
    file: str


@dataclass
class Zip:
    left: TypeInner
    right: TypeInner
    lineno: str
    file: str


@dataclass
class Reduce:
    inner: TypeInner
    fn: NadaFunction[T, R]
    lineno: str
    file: str


@dataclass
class Unzip:
    inner: TypeInner
    lineno: str
    file: str


def unzip(array='Array[NadaTuple[T, R]]') -> 'NadaTuple[Array[T], Array[R]]':
    from future.nada_types.collections import NadaTuple, Array
    right_type = Array.generic_type(array.inner_type.right_type, size=array.size)
    left_type = Array.generic_type(array.inner_type.left_type, size=array.size)

    return NadaTuple(right_type=right_type, left_type=left_type, inner=Unzip(inner=array, **get_back_file_lineno()))
