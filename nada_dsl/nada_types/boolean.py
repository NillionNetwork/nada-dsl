from typing import Union
from dataclasses import dataclass
from typing import Literal
from . import NadaType
from nada_dsl.operations import (
    Equals,
)
from nada_dsl.source_ref import SourceRef


@dataclass
class Boolean(NadaType):
    value: bool

    def __init__(self, value: int):
        super().__init__(inner=Literal(value=value, source_ref=SourceRef.back_frame()))
        if isinstance(value, int):
            self.value = value
        else:
            raise ValueError(f"Expected a boolean, got {type(value).__name__}")

    def __eq__(self, other: Union["PublicBoolean", "Boolean"]) -> Union["PublicBoolean", "Boolean"]:
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBoolean):
            return PublicBoolean(inner=operation)
        elif isinstance(other, Boolean):
            return Boolean(value=self.value == other.value)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")

@dataclass
class SecretBoolean(NadaType):
    pass


@dataclass
class PublicBoolean(NadaType):
    def __eq__(self, other: Union["PublicBoolean", "Boolean"]) -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicBoolean) or isinstance(other, Boolean):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
