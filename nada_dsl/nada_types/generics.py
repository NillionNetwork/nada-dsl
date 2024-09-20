"""Generic type definitions for Nada."""

from typing import TypeVar

from nada_dsl.nada_types import NadaType

R = TypeVar("R", bound=NadaType)
T = TypeVar("T", bound=NadaType)
U = TypeVar("U", bound=NadaType)
