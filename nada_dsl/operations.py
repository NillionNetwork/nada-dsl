"""
Class definitions corresponding to Nada operations.
"""

from dataclasses import dataclass
from nada_dsl import SourceRef
from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    IfElseASTOperation,
    RandomASTOperation,
    UnaryASTOperation,
)
from nada_dsl.nada_types.collections import Array, ArrayType, Tuple
from nada_dsl.nada_types.generics import T, R
from nada_dsl.nada_types import AllTypes


class BinaryOperation:
    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = id(self)
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            left=self.left.inner.id,
            right=self.right.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class UnaryOperation:
    def __init__(self, inner: AllTypes, source_ref: SourceRef):
        self.id = id(self)
        self.inner = inner
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        AST_OPERATIONS[self.id] = UnaryASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            inner=self.inner.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Addition(BinaryOperation):
    pass


class Subtraction(BinaryOperation):
    pass


class Multiplication(BinaryOperation):
    pass


class Division(BinaryOperation):
    pass


class Modulo(BinaryOperation):
    pass


class Power(BinaryOperation):
    pass


class RightShift(BinaryOperation):
    pass


class LeftShift(BinaryOperation):
    pass


class LessThan(BinaryOperation):
    pass


class GreaterThan(BinaryOperation):
    pass


class LessOrEqualThan(BinaryOperation):
    pass


class GreaterOrEqualThan(BinaryOperation):
    pass


class Equals(BinaryOperation):
    pass


class PublicOutputEquality(BinaryOperation):
    pass


class Unzip(UnaryOperation):
    pass


class Random:
    source_ref: SourceRef

    def __init__(self, source_ref):
        self.id = id(self)
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        AST_OPERATIONS[self.id] = RandomASTOperation(
            id=self.id, ty=ty, source_ref=self.source_ref
        )


@dataclass
class IfElse:
    """
    cond.if_else(left, right)
    """

    this: AllTypes  # cond
    arg_0: AllTypes  # left
    arg_1: AllTypes  # right
    source_ref: SourceRef

    def __init__(
        self, this: AllTypes, arg_0: AllTypes, arg_1: AllTypes, source_ref: SourceRef
    ):
        self.id = id(self)
        self.this = this
        self.arg_0 = arg_0
        self.arg_1 = arg_1
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        AST_OPERATIONS[self.id] = IfElseASTOperation(
            id=self.id,
            this=self.this.inner.id,
            arg_0=self.arg_0.inner.id,
            arg_1=self.arg_1.inner.id,
            ty=ty,
            source_ref=self.source_ref,
        )


class Reveal(UnaryOperation):
    def __init__(self, this: AllTypes, source_ref: SourceRef):
        super().__init__(inner=this, source_ref=source_ref)


class TruncPr(BinaryOperation):
    pass


def unzip(array: Array[Tuple[T, R]]) -> Tuple[Array[T], Array[R]]:
    right_type = ArrayType(inner_type=array.inner_type.right_type, size=array.size)
    left_type = ArrayType(inner_type=array.inner_type.left_type, size=array.size)

    return Tuple(
        right_type=right_type,
        left_type=left_type,
        inner=Unzip(inner=array, source_ref=SourceRef.back_frame()),
    )


class Not(UnaryOperation):
    def __init__(self, this: AllTypes, source_ref: SourceRef):
        super().__init__(inner=this, source_ref=source_ref)
