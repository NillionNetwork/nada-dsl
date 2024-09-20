"""Tests for NadaType."""

import pytest
from nada_dsl.nada_types import NadaType
from nada_dsl.nada_types.scalar_types import Integer, PublicBoolean, SecretInteger


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (SecretInteger, "SecretInteger"),
        (Integer, "Integer"),
        (PublicBoolean, "Boolean"),
    ],
)
def test_class_to_type(cls: NadaType, expected: str):
    """Tests `NadaType.class_to_type()"""
    assert cls.class_to_type() == expected
