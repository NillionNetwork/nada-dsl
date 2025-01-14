"""AST utilities."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
from typing import Dict, List
from sortedcontainers import SortedDict
from betterproto.lib.google.protobuf import Empty

from nada_mir_proto.nillion.nada.operations import v1 as proto_op
from nada_mir_proto.nillion.nada.types import v1 as proto_ty
from nada_mir_proto.nillion.nada.mir import v1 as proto_mir

from nada_dsl.nada_types import Party
from nada_dsl.source_ref import SourceRef


class OperationId:
    """Operation identifier generator."""

    current = 0

    @classmethod
    def next(cls):
        """Returns the next operation identifier."""
        next_op_id = cls.current
        cls.current += 1
        return next_op_id

    @classmethod
    def reset(cls):
        """Resets the operation identifier generator."""
        cls.current = 0


@dataclass
class ASTOperation(ABC):
    """AST Operations.

    Base abstract class for all AST Operations. Defines the minimum contract
    that needs to be implemented by any subclass.

    Attributes
    ----------
    id: int
        The operation identifier. This is the unique identifier assigned by Python
        that is the return value of id().

    source_ref: SourceRef
        The source reference object

    ty: str | Dict[str, Dict]
        The type representation, it can be a string (e.g. "SecretInteger") or a dictionary
        for compount types.
    """

    id: int
    source_ref: SourceRef
    ty: proto_ty.NadaType

    @abstractmethod
    def child_operations(self) -> List[int]:
        """Returns the list of identifiers of all the child operations of this operation."""
        raise NotImplementedError("Operation should implement child_operations method")

    @abstractmethod
    def to_mir(self) -> proto_op.Operation:
        """Converts this AST Operation into a valid MIR data structure"""
        raise NotImplementedError("Operation should implement to_mir method")


# Map of operations identified by the Python compiler
# The key is the operation identifier, the value the operation
AST_OPERATIONS: Dict[int, ASTOperation] = SortedDict()

# Map of literal hashes to index
LITERALS: Dict[str, int] = {}


@dataclass
class BinaryASTOperation(ASTOperation):
    """Superclass of all the Binary operations in AST representation"""

    variant: proto_op.BinaryOperationVariant
    left: int
    right: int

    def child_operations(self) -> List[int]:
        return [self.left, self.right]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            binary=proto_op.BinaryOperation(
                variant=self.variant,
                left=self.left,
                right=self.right,
            ),
        )


@dataclass
class UnaryASTOperation(ASTOperation):
    """Superclass of all the unary operations in AST representation"""

    variant: proto_op.UnaryOperationVariant
    child: int

    def child_operations(self):
        return [self.child]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            unary=proto_op.UnaryOperation(
                variant=self.variant,
                this=self.child,
            ),
        )


@dataclass
class IfElseASTOperation(ASTOperation):
    """AST Representation of an IfElse operation."""

    condition: int
    true_branch_child: int
    false_branch_child: int

    def child_operations(self):
        return [self.condition, self.true_branch_child, self.false_branch_child]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            ifelse=proto_op.IfElseOperation(
                cond=self.condition,
                first=self.true_branch_child,
                second=self.false_branch_child,
            ),
        )


@dataclass
class RandomASTOperation(ASTOperation):
    """AST Representation of a Random operation."""

    def child_operations(self):
        return []

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            random=Empty(),
        )


@dataclass
class InputASTOperation(ASTOperation):
    """AST representation of an Input."""

    name: str
    party: Party
    doc: str

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            input_ref=proto_op.InputReference(
                refers_to=self.name,
            ),
        )

    def child_operations(self) -> List[int]:
        return []


@dataclass
class LiteralASTOperation(ASTOperation):
    """AST Representation of a Literal."""

    name: str
    value: object
    literal_index: str

    def __init__(
        self,
        operation_id: int,
        name: str,
        ty: str | Dict[str, Dict],
        value: object,
        source_ref: SourceRef,
    ):
        self.id = operation_id
        self.name = name
        self.ty = ty
        self.value = value
        self.source_ref = source_ref
        # Generate a unique name depending on the value and type
        # to prevent duplicating literals in the bytecode.
        literal_name = hashlib.md5(
            (str(self.value) + str(self.ty)).encode("UTF-8")
        ).hexdigest()

        # Replace the literal name by an index so it is shorter
        if literal_name not in LITERALS:
            LITERALS[literal_name] = len(LITERALS)

        self.literal_index = str(LITERALS[literal_name])

        super().__init__(id=self.id, source_ref=self.source_ref, ty=self.ty)

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            literal_ref=proto_op.LiteralReference(
                refers_to=self.literal_index,
            ),
        )

    def child_operations(self) -> List[int]:
        return []


@dataclass
class ReduceASTOperation(ASTOperation):
    """AST Representation of a Reduce operation."""

    child: int
    fn: int
    initial: int

    def child_operations(self):
        return [self.child, self.initial]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            reduce=proto_op.ReduceOperation(
                fn=self.fn,
                child=self.child,
                initial=self.initial,
            ),
        )


@dataclass
class MapASTOperation(ASTOperation):
    """AST representation of a Map operation."""

    child: int
    fn: int

    def child_operations(self):
        return [self.child]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            map=proto_op.MapOperation(
                fn=self.fn,
                child=self.child,
            ),
        )


@dataclass
class NewASTOperation(ASTOperation):
    """AST Representation of a New operation."""

    name: str
    elements: List[int]

    def child_operations(self):
        return self.elements

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            new=proto_op.NewOperation(
                elements=self.elements,
            ),
        )


@dataclass
class NadaFunctionArgASTOperation(ASTOperation):
    """AST representation of a NadaFunctionArg operation."""

    name: str
    fn: int

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            arg_ref=proto_op.NadaFunctionArgRef(
                function_id=self.fn,
                refers_to=self.name,
            ),
        )

    def child_operations(self) -> List[int]:
        return []


@dataclass
class NadaFunctionASTOperation(ASTOperation):
    """AST representation of a nada function."""

    name: str
    args: List[int]
    child: int

    # pylint: disable=arguments-differ
    def to_mir(self, operations):
        """Convert a function to MIR."""
        args: List[proto_mir.NadaFunctionArg] = [
            proto_mir.NadaFunctionArg(
                name=AST_OPERATIONS[arg].name,
                type=AST_OPERATIONS[arg].ty,
                source_ref_index=AST_OPERATIONS[arg].source_ref.to_index(),
            )
            for arg in self.args
        ]  # type: ignore
        return proto_mir.NadaFunction(
            id=self.id,
            args=args,
            name=self.name,
            return_operation_id=self.child,
            operations=operations,
            return_type=self.ty,
            source_ref_index=self.source_ref.to_index(),
        )

    def __hash__(self) -> int:
        return self.id

    def child_operations(self) -> List[int]:
        return self.args + [self.child]


# Partially implemented
@dataclass
class CastASTOperation(ASTOperation):
    """AST Representation of a Cast operation."""

    target: int

    def child_operations(self):
        return [self.target]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            cast=proto_op.CastOperation(
                target=self.target,
                cast_to=self.ty,
            ),
        )


@dataclass
class TupleAccessorASTOperation(ASTOperation):
    """AST representation of a tuple accessor operation."""

    index: int
    source: int

    def child_operations(self):
        return [self.source]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            tuple_accessor=proto_op.TupleAccessor(
                index=proto_op.TupleIndex.LEFT
                if self.index == 0
                else proto_op.TupleIndex.RIGHT,
            ),
        )


@dataclass
class NTupleAccessorASTOperation(ASTOperation):
    """AST representation of a n tuple accessor operation."""

    index: int
    source: int

    def child_operations(self):
        return [self.source]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            ntuple_accessor=proto_op.NtupleAccessor(
                index=self.index,
                source=self.source,
            ),
        )


@dataclass
class ObjectAccessorASTOperation(ASTOperation):
    """AST representation of an object accessor operation."""

    key: str
    source: int

    def child_operations(self):
        return [self.source]

    def to_mir(self) -> proto_op.Operation:
        return proto_op.Operation(
            id=self.id,
            type=self.ty,
            source_ref_index=self.source_ref.to_index(),
            object_accessor=proto_op.ObjectAccessor(
                key=self.key,
                source=self.source,
            ),
        )
