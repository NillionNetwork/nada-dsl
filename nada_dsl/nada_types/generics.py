"""Generic type definitions for Nada."""

from typing import TypeVar

from nada_dsl.nada_types import DslType

R = TypeVar("R", bound=DslType)
T = TypeVar("T", bound=DslType)
U = TypeVar("U", bound=DslType)
