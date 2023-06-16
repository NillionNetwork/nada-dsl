from dataclasses import dataclass

from . import NadaType


@dataclass
class SecretString(NadaType):
    pass


@dataclass
class PublicString(NadaType):
    pass
