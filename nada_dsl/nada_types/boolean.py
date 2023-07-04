from dataclasses import dataclass
from . import NadaType
from nada_dsl.operations import (
    Equals,
)
from nada_dsl.source_ref import SourceRef


@dataclass
class SecretBoolean(NadaType):
    pass


@dataclass
class PublicBoolean(NadaType):
    def __eq__(self, other: "PublicBoolean") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBoolean):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
