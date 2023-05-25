from dataclasses import dataclass

from nada_dsl import SourceRef
from nada_dsl.nada_types import AllTypes, AllTypesType


@dataclass
class Cast:
    target: AllTypes
    to: AllTypesType
    source_ref: SourceRef
