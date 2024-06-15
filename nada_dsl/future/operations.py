from dataclasses import dataclass

from nada_dsl import SourceRef
from nada_dsl.ast_util import AST_OPERATIONS, CastASTOperation
from nada_dsl.nada_types import AllTypes, AllTypesType


@dataclass
class Cast:
    target: AllTypes
    to: AllTypesType
    source_ref: SourceRef

    def __init__(self, target: AllTypes, to: AllTypes, source_ref: SourceRef):
        self.id = id(self)
        self.target = target
        self.to = to
        self.source_ref = source_ref

    def store_in_ast(self, ty: object):
        # We don't need to use ty because the output type is part of the operation.
        AST_OPERATIONS[self.id] = CastASTOperation(
            id=self.id, target=self.target, to=self.to, source_ref=self.source_ref
        )
