"""Operations that will be supported in the future."""

from dataclasses import dataclass

from nada_mir_proto.nillion.nada.types import v1 as proto_ty

from nada_dsl import SourceRef
from nada_dsl.ast_util import AST_OPERATIONS, CastASTOperation, OperationId
from nada_dsl.nada_types import AllTypes, AllTypesType


@dataclass
class Cast:
    """Cast operation."""

    target: AllTypes
    to: AllTypesType
    source_ref: SourceRef

    def __init__(self, target: AllTypes, to: AllTypes, source_ref: SourceRef):
        self.id = OperationId.next()
        self.target = target
        self.to = to
        self.source_ref = source_ref

    def store_in_ast(self, ty: proto_ty.NadaType):
        """Store object in AST"""
        AST_OPERATIONS[self.id] = CastASTOperation(
            id=self.id, target=self.target, ty=ty, source_ref=self.source_ref
        )
