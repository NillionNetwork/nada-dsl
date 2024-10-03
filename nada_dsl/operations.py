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
    next_operation_id,
)
from nada_dsl.nada_types import AllTypes


class BinaryOperation:
    """Superclass of all the binary operations."""

    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = next_operation_id()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        """Store object in AST"""
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            left=self.left.inner.id,
            right=self.right.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class UnaryOperation:
    """Superclass of all the unary operations."""

    def __init__(self, inner: AllTypes, source_ref: SourceRef):
        self.id = next_operation_id()
        self.inner = inner
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        """Store object in AST."""
        AST_OPERATIONS[self.id] = UnaryASTOperation(
            id=self.id,
            name=self.__class__.__name__,
            inner=self.inner.inner.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Addition(BinaryOperation):
    """Addition operation"""


class Subtraction(BinaryOperation):
    """Subtraction operation."""


class Multiplication(BinaryOperation):
    """Multiplication operation"""


class Division(BinaryOperation):
    """Division operation"""


class Modulo(BinaryOperation):
    """Modulo operation"""


class Power(BinaryOperation):
    """Power operation"""


class RightShift(BinaryOperation):
    """Right shift (>>) operation."""


class LeftShift(BinaryOperation):
    """Left shift (<<)operation."""


class LessThan(BinaryOperation):
    """Less than (<) operation"""


class GreaterThan(BinaryOperation):
    """Greater than (>) operation."""


class LessOrEqualThan(BinaryOperation):
    """Less or equal (<=) operation."""


class GreaterOrEqualThan(BinaryOperation):
    """Greater or equal (>=) operation."""


class Equals(BinaryOperation):
    """Equals (==) operation"""


class NotEquals(BinaryOperation):
    """Not equals (!=) operation."""


class PublicOutputEquality(BinaryOperation):
    """Public output equality operation."""


class BooleanAnd(BinaryOperation):
    """Boolean AND (&) operation."""


class BooleanOr(BinaryOperation):
    """Boolean OR (|) operation."""


class BooleanXor(BinaryOperation):
    """Boolean XOR (^) operation."""


class Random:
    """Random operation."""

    source_ref: SourceRef

    def __init__(self, source_ref):
        self.id = next_operation_id()
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        """Store object in AST."""
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
        self.id = next_operation_id()
        self.this = this
        self.arg_0 = arg_0
        self.arg_1 = arg_1
        self.source_ref = source_ref

    def store_in_ast(self, ty):
        """Store object in AST."""
        AST_OPERATIONS[self.id] = IfElseASTOperation(
            id=self.id,
            this=self.this.inner.id,
            arg_0=self.arg_0.inner.id,
            arg_1=self.arg_1.inner.id,
            ty=ty,
            source_ref=self.source_ref,
        )


class Reveal(UnaryOperation):
    """Reveal (i.e. make public) operation."""

    def __init__(self, this: AllTypes, source_ref: SourceRef):
        super().__init__(inner=this, source_ref=source_ref)


class TruncPr(BinaryOperation):
    """Probabilistic Truncation operation."""


class Not(UnaryOperation):
    """Not (!) Operation"""

    def __init__(self, this: AllTypes, source_ref: SourceRef):
        super().__init__(inner=this, source_ref=source_ref)
