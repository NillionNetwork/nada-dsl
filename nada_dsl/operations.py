"""
Class definitions corresponding to Nada operations.
"""

from dataclasses import dataclass
from nada_mir_proto.nillion.nada.types import v1 as proto_ty
from nada_mir_proto.nillion.nada.operations import v1 as proto_op

from nada_dsl import SourceRef
from nada_dsl.ast_util import (
    AST_OPERATIONS,
    BinaryASTOperation,
    IfElseASTOperation,
    RandomASTOperation,
    UnaryASTOperation,
    OperationId,
)
from nada_dsl.nada_types import AllTypes


class BinaryOperation:
    """Superclass of all the binary operations."""

    variant: proto_op.BinaryOperationVariant

    def __init__(self, left: AllTypes, right: AllTypes, source_ref: SourceRef):
        self.id = OperationId.next()
        self.left = left
        self.right = right
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store object in AST"""
        AST_OPERATIONS[self.id] = BinaryASTOperation(
            id=self.id,
            variant=self.variant,
            left=self.left.child.id,
            right=self.right.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class UnaryOperation:
    """Superclass of all the unary operations."""

    variant: proto_op.UnaryOperationVariant

    def __init__(self, child: AllTypes, source_ref: SourceRef):
        self.id = OperationId.next()
        self.child = child
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store object in AST."""
        AST_OPERATIONS[self.id] = UnaryASTOperation(
            id=self.id,
            variant=self.variant,
            child=self.child.child.id,
            source_ref=self.source_ref,
            ty=ty,
        )


class Addition(BinaryOperation):
    """Addition operation"""

    variant = proto_op.BinaryOperationVariant.ADDITION


class Subtraction(BinaryOperation):
    """Subtraction operation."""

    variant = proto_op.BinaryOperationVariant.SUBTRACTION


class Multiplication(BinaryOperation):
    """Multiplication operation"""

    variant = proto_op.BinaryOperationVariant.MULTIPLICATION


class Division(BinaryOperation):
    """Division operation"""

    variant = proto_op.BinaryOperationVariant.DIVISION


class Modulo(BinaryOperation):
    """Modulo operation"""

    variant = proto_op.BinaryOperationVariant.MODULO


class Power(BinaryOperation):
    """Power operation"""

    variant = proto_op.BinaryOperationVariant.POWER


class RightShift(BinaryOperation):
    """Right shift (>>) operation."""

    variant = proto_op.BinaryOperationVariant.RIGHT_SHIFT


class LeftShift(BinaryOperation):
    """Left shift (<<)operation."""

    variant = proto_op.BinaryOperationVariant.LEFT_SHIFT


class LessThan(BinaryOperation):
    """Less than (<) operation"""

    variant = proto_op.BinaryOperationVariant.LESS_THAN


class GreaterThan(BinaryOperation):
    """Greater than (>) operation."""

    variant = proto_op.BinaryOperationVariant.GREATER_THAN


class LessOrEqualThan(BinaryOperation):
    """Less or equal (<=) operation."""

    variant = proto_op.BinaryOperationVariant.LESS_EQ


class GreaterOrEqualThan(BinaryOperation):
    """Greater or equal (>=) operation."""

    variant = proto_op.BinaryOperationVariant.GREATER_EQ


class Equals(BinaryOperation):
    """Equals (==) operation"""

    variant = proto_op.BinaryOperationVariant.EQUALS


class NotEquals(BinaryOperation):
    """Not equals (!=) operation."""

    variant = proto_op.BinaryOperationVariant.NOT_EQUALS


class PublicOutputEquality(BinaryOperation):
    """Public output equality operation."""

    variant = proto_op.BinaryOperationVariant.EQUALS_PUBLIC_OUTPUT


class BooleanAnd(BinaryOperation):
    """Boolean AND (&) operation."""

    variant = proto_op.BinaryOperationVariant.BOOL_AND


class BooleanOr(BinaryOperation):
    """Boolean OR (|) operation."""

    variant = proto_op.BinaryOperationVariant.BOOL_OR


class BooleanXor(BinaryOperation):
    """Boolean XOR (^) operation."""

    variant = proto_op.BinaryOperationVariant.BOOL_XOR


class Random:
    """Random operation."""

    source_ref: SourceRef

    def __init__(self, source_ref):
        self.id = OperationId.next()
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
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
        self.id = OperationId.next()
        self.this = this
        self.arg_0 = arg_0
        self.arg_1 = arg_1
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store object in AST."""
        AST_OPERATIONS[self.id] = IfElseASTOperation(
            id=self.id,
            condition=self.this.child.id,
            true_branch_child=self.arg_0.child.id,
            false_branch_child=self.arg_1.child.id,
            ty=ty,
            source_ref=self.source_ref,
        )


class Reveal(UnaryOperation):
    """Reveal (i.e. make public) operation."""

    variant = proto_op.UnaryOperationVariant.REVEAL

    def __init__(self, this: AllTypes, source_ref: SourceRef):
        super().__init__(child=this, source_ref=source_ref)


class TruncPr(BinaryOperation):
    """Probabilistic Truncation operation."""

    variant = proto_op.BinaryOperationVariant.TRUNC_PR


class Not(UnaryOperation):
    """Not (!) Operation"""

    variant = proto_op.UnaryOperationVariant.NOT

    def __init__(self, this: AllTypes, source_ref: SourceRef):
        super().__init__(child=this, source_ref=source_ref)


class EcdsaSign(BinaryOperation):
    """Ecdsa signing operation."""

    variant = proto_op.BinaryOperationVariant.ECDSA_SIGN
