from dataclasses import dataclass
from typing import Union

from nada_dsl.nada_types.boolean import PublicBoolean, SecretBoolean, Boolean
from nada_dsl.operations import (
    Addition,
    Division,
    Equals,
    GreaterOrEqualThan,
    GreaterThan,
    LeftShift,
    LessOrEqualThan,
    LessThan,
    Modulo,
    Power,
    Multiplication,
    RightShift,
    Subtraction,
)
from nada_dsl.source_ref import SourceRef
from nada_dsl.circuit_io import Literal

from . import NadaType


@dataclass
class Integer(NadaType):
    value: int

    def __init__(self, value: int):
        super().__init__(inner=Literal(value=value, source_ref=SourceRef.back_frame()))
        if isinstance(value, int):
            self.value = value
        else:
            raise ValueError(f"Expected an integer, got {type(value).__name__}")

    def __add__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> Union["SecretInteger", "PublicInteger", "Integer"]:
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value + other.value)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> Union["SecretInteger", "PublicInteger", "Integer"]:
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value - other.value)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> Union["SecretInteger", "PublicInteger", "Integer"]:
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value * other.value)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __truediv__(self, other: Union["PublicInteger", "Integer"]) -> Union["PublicInteger", "Integer"]:
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value / other.value)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: Union["PublicInteger", "Integer"]) -> Union["PublicInteger", "Integer"]:
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value % other.value)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __pow__(self, other: Union["PublicInteger", "Integer"]) -> Union["PublicInteger", "Integer"]:
        operation = Power(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value ** other.value)
        else:
            raise TypeError(f"Invalid operation: {self} ** {other}")

    def __rshift__(self, other: Union["PublicInteger", "Integer"]) -> Union["PublicInteger", "Integer"]:
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value >> other.value)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(self, other: Union["PublicInteger", "Integer"]) -> Union["PublicInteger", "Integer"]:
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicInteger(inner=operation)
        elif isinstance(other, Integer):
            return Integer(value=self.value << other.value)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: Union["PublicInteger", "Integer"]) -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, Integer):
            return Boolean(value=self.value < other.value)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, Integer):
            return Boolean(value=self.value > other.value)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, Integer):
            return Boolean(value=self.value <= other.value)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, Integer):
            return Boolean(value=self.value >= other.value)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger):
            return PublicBoolean(inner=operation)
        elif isinstance(other, Integer):
            return Boolean(value=self.value == other.value)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")

@dataclass
class SecretInteger(NadaType):
    def __add__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> "SecretInteger":
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if (
            isinstance(other, SecretInteger)
            or isinstance(other, PublicInteger)
            or isinstance(other, Integer)
        ):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> "SecretInteger":
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if (
            isinstance(other, SecretInteger)
            or isinstance(other, PublicInteger)
            or isinstance(other, Integer)
        ):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> "SecretInteger":
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if (
            isinstance(other, SecretInteger)
            or isinstance(other, PublicInteger)
            or isinstance(other, Integer)
        ):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __lt__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "SecretInteger") -> "SecretBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")
    
    def __mod__(self, other: "PublicInteger") -> "SecretInteger":
        """Modulo operation for SecretInteger.

        Only public variable or literal divisor is supported.

        :param other: The modulo divisor, must be a public integer.
        :type other: PublicInteger
        :raises TypeError: Raised when the divisor type is not PublicInteger
        :return: The modulo result as a Secret Integer
        :rtype: SecretInteger
        """
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")
        
    def __pow__(self, other: "PublicInteger") -> "SecretInteger":
        operation = Power(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return SecretInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} ** {other}")


@dataclass
class PublicInteger(NadaType):
    def __add__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> Union["SecretInteger", "PublicInteger"]:
        operation = Addition(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} + {other}")

    def __sub__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> Union["SecretInteger", "PublicInteger"]:
        operation = Subtraction(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} - {other}")

    def __mul__(
        self, other: Union["SecretInteger", "PublicInteger", "Integer"]
    ) -> Union["SecretInteger", "PublicInteger"]:
        operation = Multiplication(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, SecretInteger):
            return SecretInteger(inner=operation)
        elif isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} * {other}")

    def __truediv__(self, other: "PublicInteger") -> "PublicInteger":
        operation = Division(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} / {other}")

    def __mod__(self, other: "PublicInteger") -> "PublicInteger":
        operation = Modulo(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} % {other}")

    def __rshift__(self, other: "PublicInteger") -> "PublicInteger":
        operation = RightShift(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >> {other}")

    def __lshift__(self, other: "PublicInteger") -> "PublicInteger":
        operation = LeftShift(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicInteger(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} << {other}")

    def __lt__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = LessThan(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} < {other}")

    def __gt__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = GreaterThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} > {other}")

    def __le__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = LessOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} <= {other}")

    def __ge__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = GreaterOrEqualThan(
            left=self, right=other, source_ref=SourceRef.back_frame()
        )
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} >= {other}")

    def __eq__(self, other: "PublicInteger") -> "PublicBoolean":
        operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
        if isinstance(other, PublicInteger) or isinstance(other, Integer):
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")
