"""Operations that will be supported in the future."""

from dataclasses import dataclass

from nada_dsl import SourceRef
from nada_dsl.ast_util import AST_OPERATIONS, CastASTOperation, next_operation_id
from nada_dsl.nada_types import AllTypes, AllTypesType


@dataclass
class Cast:
    """Cast operation."""

    target: AllTypes
    to: AllTypesType
    source_ref: SourceRef

    def __init__(self, target: AllTypes, to: AllTypes, source_ref: SourceRef):
        self.id = next_operation_id()
        self.target = target
        self.to = to
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        """Store object in AST"""
        AST_OPERATIONS[self.id] = CastASTOperation(
            id=self.id, target=self.target, ty=ty, source_ref=self.source_ref
        )
